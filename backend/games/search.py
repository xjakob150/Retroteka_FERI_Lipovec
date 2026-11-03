import logging

from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone

from .igdb import IGDBError, get_client
from .models import Game, GameRelease, Platform

PAGE_SIZE = 20

logger = logging.getLogger(__name__)


def save_games(igdb_games):
    """Zapiše igre iz odjemalca IGDB v bazo in jih vrne v enakem vrstnem redu (ADR-0006)."""
    platform_ids = {release['platform_igdb_id'] for game in igdb_games for release in game['releases']}
    platforms = {
        platform.igdb_id: platform
        for platform in Platform.objects.filter(igdb_id__in=platform_ids, is_supported=True)
    }
    synced_at = timezone.now()
    games = []
    with transaction.atomic():
        for data in igdb_games:
            game, _ = Game.objects.update_or_create(
                igdb_id=data['igdb_id'],
                defaults={
                    'title': data['title'],
                    'cover_url': data['cover_url'],
                    'release_year': data['release_year'],
                    'genres': data['genres'],
                    'summary': data['summary'],
                    'synced_at': synced_at,
                },
            )
            # Izdaje se samo dodajajo in posodabljajo; izdaja, ki je IGDB ne vrne več, ostane,
            # da izvodi na tej platformi ostanejo veljavni.
            for release in data['releases']:
                platform = platforms.get(release['platform_igdb_id'])
                if platform is None:
                    continue
                year = release['release_year']
                GameRelease.objects.update_or_create(
                    game=game,
                    platform=platform,
                    defaults={'release_year': year} if year is not None else {},
                )
            games.append(game)
    return games


def search_saved_games(query, limit=20, offset=0):
    """Rezerva ob izpadu IGDB: vrne (igre, skupno število) iz shranjenih iger."""
    games = Game.objects.filter(releases__platform__is_supported=True)
    # Vsaka beseda mora biti v naslovu, vrstni red in velike črke niso pomembni.
    for word in query.split():
        games = games.filter(title__icontains=word)
    games = games.distinct().order_by('title', 'id')
    return list(games[offset:offset + limit]), games.count()


def search_games(query, page):
    """Vrne (igre, skupno število, ali so to shranjeni podatki) za eno stran iskanja."""
    offset = (page - 1) * PAGE_SIZE
    supported = Platform.objects.filter(is_supported=True).values_list('igdb_id', flat=True)
    try:
        igdb_games, total = get_client().search(query, supported, limit=PAGE_SIZE, offset=offset)
        games, saved_data = save_games(igdb_games), False
    except IGDBError as error:
        logger.warning('IGDB search failed, using saved games: %s', error)
        (games, total), saved_data = search_saved_games(query, limit=PAGE_SIZE, offset=offset), True
    return with_supported_releases(games), total, saved_data


def with_supported_releases(games):
    # Naloži izdaje vseh iger z eno poizvedbo in ohrani vrstni red iskanja.
    releases = GameRelease.objects.filter(platform__is_supported=True).select_related('platform')
    loaded = Game.objects.filter(pk__in=[game.pk for game in games]).prefetch_related(
        Prefetch('releases', queryset=releases.order_by('platform__generation', 'platform__name')),
    )
    by_pk = {game.pk: game for game in loaded}
    return [by_pk[game.pk] for game in games]
