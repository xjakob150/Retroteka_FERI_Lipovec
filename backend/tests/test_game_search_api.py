import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APIClient

from collection.models import Collection, CollectionItem
from games import search
from games.igdb import IGDBError
from games.models import Game, Platform
from games.search import save_games

pytestmark = pytest.mark.django_db

PS1, PS2, PS5 = 7, 8, 167


class FakeIGDB:
    def __init__(self, games=(), total=None, error=None):
        self.games, self.total, self.error = list(games), total, error
        self.calls = []

    def search(self, query, platform_ids, limit, offset):
        self.calls.append({'query': query, 'platform_ids': set(platform_ids), 'limit': limit, 'offset': offset})
        if self.error:
            raise self.error
        return self.games, len(self.games) if self.total is None else self.total


@pytest.fixture(autouse=True)
def clear_throttle_counts():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def platforms():
    Platform.objects.create(igdb_id=PS1, name='PlayStation', abbreviation='PS1', generation=5, is_supported=True)
    Platform.objects.create(igdb_id=PS2, name='PlayStation 2', abbreviation='PS2', generation=6, is_supported=True)
    Platform.objects.create(igdb_id=PS5, name='PlayStation 5', abbreviation='PS5', generation=9)


@pytest.fixture
def igdb(monkeypatch):
    def use(**kwargs):
        fake = FakeIGDB(**kwargs)
        monkeypatch.setattr(search, 'get_client', lambda: fake)
        return fake
    return use


def igdb_game(igdb_id=1601, title='Gran Turismo 4', releases=((PS2, 2004), (PS1, 2003))):
    return {
        'igdb_id': igdb_id, 'title': title, 'cover_url': 'https://images.igdb.com/x.jpg', 'release_year': 2003,
        'genres': ['Racing'], 'summary': 'Opis.',
        'releases': [{'platform_igdb_id': platform, 'release_year': year} for platform, year in releases],
    }


def get(**params):
    return APIClient().get(reverse('game-search'), params)


def test_guest_search_returns_results_from_igdb_and_stores_them(igdb):
    igdb(games=[igdb_game()], total=34)
    response = get(q='gran turismo')
    assert response.status_code == 200
    game = Game.objects.get(igdb_id=1601)
    assert response.data == {
        'count': 34,
        'page': 1,
        'saved_data': False,
        'results': [{
            'id': game.id,
            'title': 'Gran Turismo 4',
            'cover_url': 'https://images.igdb.com/x.jpg',
            'release_year': 2003,
            'genres': ['Racing'],
            'platforms': [
                {'id': Platform.objects.get(igdb_id=PS1).id, 'name': 'PlayStation', 'abbreviation': 'PS1', 'release_year': 2003},
                {'id': Platform.objects.get(igdb_id=PS2).id, 'name': 'PlayStation 2', 'abbreviation': 'PS2', 'release_year': 2004},
            ],
        }],
    }


def test_search_asks_igdb_for_supported_platforms_and_requested_page(igdb):
    fake = igdb()
    get(q='  gran turismo  ', page=3)
    assert fake.calls == [{'query': 'gran turismo', 'platform_ids': {PS1, PS2}, 'limit': 20, 'offset': 40}]


def test_results_keep_igdb_order(igdb):
    igdb(games=[igdb_game(2, 'Zelda'), igdb_game(1, 'Asteroids')])
    assert [game['title'] for game in get(q='igra').data['results']] == ['Zelda', 'Asteroids']


def test_igdb_failure_returns_saved_games_with_flag(igdb):
    save_games([igdb_game()])
    igdb(error=IGDBError('timeout'))
    response = get(q='turismo gran')
    assert response.status_code == 200
    assert response.data['saved_data'] is True
    assert response.data['count'] == 1
    assert response.data['results'][0]['title'] == 'Gran Turismo 4'


def test_igdb_failure_without_saved_games_returns_empty_saved_result(igdb):
    igdb(error=IGDBError('timeout'))
    assert get(q='zelda').data == {'count': 0, 'page': 1, 'results': [], 'saved_data': True}


def test_page_after_last_result_is_empty(igdb):
    igdb(games=[], total=5)
    response = get(q='zelda', page=2)
    assert response.status_code == 200
    assert (response.data['count'], response.data['results']) == (5, [])


@pytest.mark.parametrize('params', [{}, {'q': ''}, {'q': 'ab'}, {'q': '  ab  '}])
def test_query_needs_at_least_3_characters(igdb, params):
    fake = igdb()
    response = get(**params)
    assert response.status_code == 400
    assert response.data['q'] == ['Type at least 3 characters']
    assert fake.calls == []


@pytest.mark.parametrize('page', ['0', '-1', 'abc'])
def test_invalid_page_is_rejected(igdb, page):
    igdb()
    response = get(q='zelda', page=page)
    assert response.status_code == 400
    assert 'page' in response.data


def test_too_long_query_is_rejected(igdb):
    igdb()
    assert get(q='x' * 101).status_code == 400


def platform_id(igdb_id):
    return Platform.objects.get(igdb_id=igdb_id).id


def test_platform_filter_asks_igdb_for_that_platform_only(igdb):
    fake = igdb(games=[igdb_game()])
    response = get(q='gran turismo', platform=platform_id(PS2))
    assert response.status_code == 200
    assert fake.calls[0]['platform_ids'] == {PS2}


def test_filtered_result_still_lists_all_supported_platforms(igdb):
    igdb(games=[igdb_game(releases=((PS2, 2004), (PS1, 2003), (PS5, 2021)))])
    platforms = get(q='gran turismo', platform=platform_id(PS2)).data['results'][0]['platforms']
    assert [platform['abbreviation'] for platform in platforms] == ['PS1', 'PS2']


def test_platform_filter_applies_to_saved_games(igdb):
    save_games([igdb_game(1, 'Gran Turismo 2', releases=((PS1, 1999),)), igdb_game(2, 'Gran Turismo 4')])
    igdb(error=IGDBError('timeout'))
    response = get(q='gran turismo', platform=platform_id(PS1))
    assert response.data['saved_data'] is True
    assert [game['title'] for game in response.data['results']] == ['Gran Turismo 2', 'Gran Turismo 4']
    response = get(q='gran turismo 2', platform=platform_id(PS2))
    assert response.data['results'] == []


@pytest.mark.parametrize('value', ['unsupported', 'missing', 'abc'])
def test_unsupported_or_unknown_platform_is_rejected(igdb, value):
    fake = igdb()
    platform = {'unsupported': lambda: platform_id(PS5), 'missing': lambda: 99999, 'abc': lambda: 'abc'}[value]()
    response = get(q='zelda', platform=platform)
    assert response.status_code == 400
    assert response.data['platform'] == ['Select a supported platform.']
    assert fake.calls == []


def search_until_throttled(client, limit=121):
    return [client.get(reverse('game-search'), {'q': 'zelda'}).status_code for _ in range(limit)]


def test_guest_gets_429_after_120_searches_per_minute(igdb):
    fake = igdb()
    statuses = search_until_throttled(APIClient(REMOTE_ADDR='10.0.0.1'))
    assert statuses[:120] == [200] * 120
    assert statuses[120] == 429
    assert len(fake.calls) == 120


def test_guests_on_other_addresses_have_their_own_limit(igdb):
    igdb()
    search_until_throttled(APIClient(REMOTE_ADDR='10.0.0.1'))
    assert APIClient(REMOTE_ADDR='10.0.0.2').get(reverse('game-search'), {'q': 'zelda'}).status_code == 200


def test_logged_in_users_are_counted_by_account(igdb):
    igdb()
    users = [
        get_user_model().objects.create_user(name, f'{name}@example.com', 'dolgo-geslo-1') for name in ('ana', 'marko')
    ]
    clients = []
    for user in users:
        client = APIClient(REMOTE_ADDR='10.0.0.1')
        client.force_authenticate(user)
        clients.append(client)
    assert search_until_throttled(clients[0])[120] == 429
    assert clients[1].get(reverse('game-search'), {'q': 'zelda'}).status_code == 200


def logged_in(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def make_user(username='marko'):
    return get_user_model().objects.create_user(username, f'{username}@example.com', 'dolgo-geslo-1')


def own(user, collection_name, game, platform_igdb_id):
    collection, _ = Collection.objects.get_or_create(user=user, name=collection_name)
    CollectionItem.objects.create(
        collection=collection, game=game, platform=Platform.objects.get(igdb_id=platform_igdb_id),
        region='pal', condition='cib',
    )


def test_logged_in_user_sees_where_they_own_the_game(igdb):
    user = make_user()
    [game] = save_games([igdb_game()])
    own(user, 'For sale', game, PS2)
    own(user, 'For sale', game, PS2)
    own(user, 'Main shelf', game, PS1)
    igdb(games=[igdb_game(2, 'Okami', releases=((PS2, 2006),)), igdb_game()])
    results = logged_in(user).get(reverse('game-search'), {'q': 'igra'}).data['results']
    assert results[0]['owned'] == []
    assert [(entry['platform']['abbreviation'], entry['collection']['name']) for entry in results[1]['owned']] == [
        ('PS1', 'Main shelf'), ('PS2', 'For sale'),
    ]


def test_guest_gets_no_ownership_field(igdb):
    [game] = save_games([igdb_game()])
    own(make_user(), 'For sale', game, PS2)
    igdb(games=[igdb_game()])
    assert 'owned' not in get(q='gran turismo').data['results'][0]


def test_other_users_items_are_not_shown(igdb):
    [game] = save_games([igdb_game()])
    own(make_user('ana'), 'Anina', game, PS2)
    igdb(games=[igdb_game()])
    assert logged_in(make_user()).get(reverse('game-search'), {'q': 'gran'}).data['results'][0]['owned'] == []


def test_saved_data_results_also_show_ownership(igdb):
    user = make_user()
    [game] = save_games([igdb_game()])
    own(user, 'For sale', game, PS2)
    igdb(error=IGDBError('timeout'))
    data = logged_in(user).get(reverse('game-search'), {'q': 'gran turismo'}).data
    assert data['saved_data'] is True
    assert data['results'][0]['owned'][0]['collection']['name'] == 'For sale'


def test_ownership_adds_one_query_for_the_whole_page(igdb):
    user = make_user()
    games = [igdb_game(n, f'Igra {n}') for n in range(1, 11)]
    for game in save_games(games):
        own(user, 'Main shelf', game, PS2)
    igdb(games=games)

    def queries(client):
        with CaptureQueriesContext(connection) as context:
            assert client.get(reverse('game-search'), {'q': 'igra'}).status_code == 200
        return len(context)

    assert queries(logged_in(user)) - queries(APIClient()) == 1
