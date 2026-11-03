from datetime import timedelta

import pytest
from django.utils import timezone

from games.models import Game, GameRelease, Platform
from games.search import save_games, search_saved_games

pytestmark = pytest.mark.django_db

PS1, PS2, PS3 = 7, 8, 9


@pytest.fixture(autouse=True)
def platforms():
    Platform.objects.create(igdb_id=PS1, name='PlayStation', is_supported=True)
    Platform.objects.create(igdb_id=PS2, name='PlayStation 2', is_supported=True)
    Platform.objects.create(igdb_id=PS3, name='PlayStation 3', is_supported=True)
    Platform.objects.create(igdb_id=167, name='PlayStation 5', is_supported=False)


def igdb_game(igdb_id=1601, title='Gran Turismo 4', releases=((PS2, 2004),), **fields):
    return {
        'igdb_id': igdb_id,
        'title': title,
        'cover_url': 'https://images.igdb.com/igdb/image/upload/t_cover_big/co1abc.jpg',
        'release_year': 2004,
        'genres': ['Racing'],
        'summary': 'Racing simulator.',
        'releases': [{'platform_igdb_id': platform, 'release_year': year} for platform, year in releases],
        **fields,
    }


def releases(game):
    return {(release.platform.igdb_id, release.release_year) for release in game.releases.all()}


def test_new_game_and_releases_are_stored():
    [game] = save_games([igdb_game(releases=((PS2, 2004), (PS3, 2010)))])
    assert Game.objects.get().pk == game.pk
    assert game.title == 'Gran Turismo 4'
    assert game.genres == ['Racing']
    assert releases(game) == {(PS2, 2004), (PS3, 2010)}
    assert timezone.now() - game.synced_at < timedelta(seconds=5)


def test_games_are_returned_in_igdb_order():
    games = save_games([igdb_game(2, 'B'), igdb_game(1, 'A')])
    assert [game.igdb_id for game in games] == [2, 1]


def test_searching_again_updates_game_without_duplicate():
    save_games([igdb_game(title='Gran Turismo IV')])
    Game.objects.update(synced_at=timezone.now() - timedelta(days=30))
    [game] = save_games([igdb_game(title='Gran Turismo 4', summary='Novo.')])
    assert Game.objects.count() == 1
    assert (game.title, game.summary) == ('Gran Turismo 4', 'Novo.')
    assert timezone.now() - Game.objects.get().synced_at < timedelta(seconds=5)


def test_release_year_is_updated_and_new_release_added():
    save_games([igdb_game(releases=((PS2, 2005),))])
    [game] = save_games([igdb_game(releases=((PS2, 2004), (PS3, 2010)))])
    assert releases(game) == {(PS2, 2004), (PS3, 2010)}
    assert GameRelease.objects.count() == 2


def test_release_missing_from_igdb_is_kept():
    save_games([igdb_game(releases=((PS1, 2003), (PS2, 2004)))])
    [game] = save_games([igdb_game(releases=((PS2, 2004),))])
    assert releases(game) == {(PS1, 2003), (PS2, 2004)}


def test_missing_year_does_not_erase_known_year():
    save_games([igdb_game(releases=((PS2, 2004),))])
    [game] = save_games([igdb_game(releases=((PS2, None),))])
    assert releases(game) == {(PS2, 2004)}


def test_unsupported_and_unknown_platforms_are_skipped():
    [game] = save_games([igdb_game(releases=((PS2, 2004), (167, 2021), (99999, 2020)))])
    assert releases(game) == {(PS2, 2004)}


def test_empty_result_writes_nothing():
    assert save_games([]) == []
    assert not Game.objects.exists()


def titles(result):
    games, total = result
    return [game.title for game in games], total


@pytest.fixture
def saved():
    save_games([
        igdb_game(1, 'The Legend of Zelda: Ocarina of Time', releases=((PS1, 1998),)),
        igdb_game(2, 'Gran Turismo 4', releases=((PS2, 2004),)),
        igdb_game(3, 'Gran Turismo', releases=((PS1, 1997),)),
        igdb_game(4, 'Gran Turismo 7', releases=((167, 2022),)),
    ])


def test_saved_search_needs_every_word_in_any_order_and_case(saved):
    assert titles(search_saved_games('zelda OCARINA')) == (['The Legend of Zelda: Ocarina of Time'], 1)
    assert titles(search_saved_games('turismo 4 gran')) == (['Gran Turismo 4'], 1)


def test_saved_search_is_sorted_by_title(saved):
    assert titles(search_saved_games('gran turismo')) == (['Gran Turismo', 'Gran Turismo 4'], 2)


def test_saved_search_leaves_out_games_only_on_unsupported_platforms(saved):
    assert titles(search_saved_games('turismo 7')) == ([], 0)


def test_saved_search_with_unknown_word_finds_nothing(saved):
    assert titles(search_saved_games('zelda mario')) == ([], 0)


def test_saved_search_pages_and_counts_each_game_once():
    save_games([igdb_game(n, f'Mario {n:02}', releases=((PS1, 2000), (PS2, 2001))) for n in range(1, 26)])
    games, total = search_saved_games('mario', limit=20, offset=20)
    assert total == 25
    assert [game.title for game in games] == [f'Mario {n}' for n in range(21, 26)]
