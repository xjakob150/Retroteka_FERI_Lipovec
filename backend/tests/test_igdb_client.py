import threading
import time

import pytest
import requests
import responses

from games import igdb
from games.igdb import API_URL, MIN_INTERVAL, TOKEN_URL, IGDBClient, IGDBError, RateLimiter, get_client

GAMES_URL = API_URL + 'games'


@pytest.fixture
def clock(monkeypatch):
    now = {'value': 1000.0}
    monkeypatch.setattr(igdb.time, 'monotonic', lambda: now['value'])
    return now


@pytest.fixture
def client():
    return IGDBClient(client_id='id', client_secret='skrivnost', limiter=RateLimiter(0))


def add_token(token='zeton', expires_in=5_000_000):
    responses.post(TOKEN_URL, json={'access_token': token, 'expires_in': expires_in, 'token_type': 'bearer'})


def token_requests():
    return [call for call in responses.calls if call.request.url.startswith(TOKEN_URL)]


@responses.activate
def test_sends_query_with_client_id_and_token(client):
    add_token()
    responses.post(GAMES_URL, json=[{'id': 1}])
    assert client.post('games', 'fields name;').json() == [{'id': 1}]
    request = responses.calls[1].request
    assert request.headers['Client-ID'] == 'id'
    assert request.headers['Authorization'] == 'Bearer zeton'
    assert request.body == b'fields name;'


@responses.activate
def test_token_is_requested_once_for_several_requests(client, clock):
    add_token()
    responses.post(GAMES_URL, json=[])
    client.post('games', 'fields name;')
    clock['value'] += 3600
    client.post('games', 'fields name;')
    assert len(token_requests()) == 1


@responses.activate
def test_new_token_is_requested_less_than_a_minute_before_expiry(client, clock):
    add_token('prvi', expires_in=3600)
    add_token('drugi', expires_in=3600)
    responses.post(GAMES_URL, json=[])
    client.post('games', 'fields name;')
    clock['value'] += 3600 - 59
    client.post('games', 'fields name;')
    assert len(token_requests()) == 2
    assert responses.calls[-1].request.headers['Authorization'] == 'Bearer drugi'


@responses.activate
def test_rejected_token_raises_error_without_requesting_new_token(client):
    add_token()
    responses.post(GAMES_URL, status=401)
    with pytest.raises(IGDBError):
        client.post('games', 'fields name;')
    assert len(token_requests()) == 1


@responses.activate
def test_wrong_credentials_raise_error(client):
    responses.post(TOKEN_URL, status=400, json={'message': 'invalid client secret'})
    with pytest.raises(IGDBError):
        client.post('games', 'fields name;')


@responses.activate
@pytest.mark.parametrize('client_id, client_secret', [('', 'skrivnost'), ('id', '')])
def test_missing_credentials_raise_error_without_request(client_id, client_secret):
    with pytest.raises(IGDBError):
        IGDBClient(client_id=client_id, client_secret=client_secret, limiter=RateLimiter(0)).post(
            'games', 'fields name;',
        )
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.parametrize('failure', [requests.ConnectTimeout(), requests.ConnectionError()])
def test_unreachable_igdb_raises_error(client, failure):
    add_token()
    responses.post(GAMES_URL, body=failure)
    with pytest.raises(IGDBError):
        client.post('games', 'fields name;')


@responses.activate
def test_unreachable_twitch_raises_error(client):
    responses.post(TOKEN_URL, body=requests.ConnectTimeout())
    with pytest.raises(IGDBError):
        client.post('games', 'fields name;')


def test_credentials_are_read_from_environment(monkeypatch):
    monkeypatch.setenv('IGDB_CLIENT_ID', 'iz-okolja')
    monkeypatch.setenv('IGDB_CLIENT_SECRET', 'skrivnost-iz-okolja')
    client = IGDBClient()
    assert client.client_id == 'iz-okolja'
    assert client.client_secret == 'skrivnost-iz-okolja'


def test_limit_is_four_requests_per_second():
    assert MIN_INTERVAL == 0.25


def test_limiter_waits_only_for_the_rest_of_the_interval(monkeypatch, clock):
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        clock['value'] += seconds

    monkeypatch.setattr(igdb.time, 'sleep', sleep)
    limiter = RateLimiter(0.25)
    limiter.wait()
    clock['value'] += 0.1
    limiter.wait()
    clock['value'] += 1
    limiter.wait()
    assert sleeps == [pytest.approx(0.15)]


def test_limiter_spaces_requests_from_several_threads():
    limiter = RateLimiter(0.05)
    times = []

    def request():
        limiter.wait()
        times.append(time.monotonic())

    threads = [threading.Thread(target=request) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    times.sort()
    assert all(later - earlier >= 0.049 for earlier, later in zip(times, times[1:]))


@responses.activate
def test_token_request_also_waits_for_limiter(monkeypatch):
    waits = []
    limiter = RateLimiter(0)
    monkeypatch.setattr(limiter, 'wait', lambda: waits.append(True))
    add_token()
    responses.post(GAMES_URL, json=[])
    IGDBClient(client_id='id', client_secret='skrivnost', limiter=limiter).post('games', 'fields name;')
    assert len(waits) == 2


def test_clients_share_one_limiter_by_default():
    assert IGDBClient('a', 'b').limiter is IGDBClient('c', 'd').limiter


def test_get_client_returns_one_shared_client():
    assert get_client() is get_client()


# Oblika odgovora je povzeta po pravem odgovoru IGDB za "gran turismo".
GRAN_TURISMO_4 = {
    'id': 1601,
    'name': 'Gran Turismo 4',
    'cover': {'id': 1, 'image_id': 'co1abc'},
    'first_release_date': 1103846400,
    'genres': [{'id': 10, 'name': 'Racing'}, {'id': 13, 'name': 'Simulator'}],
    'summary': 'Racing simulator.',
    'platforms': [8, 167],
    'release_dates': [
        {'id': 1, 'platform': 8, 'y': 2005},
        {'id': 2, 'platform': 8, 'y': 2004},
        {'id': 3, 'platform': 167, 'y': 2021},
    ],
    'game_type': 10,
}


def search(client, query='gran turismo', platform_ids=(7, 8), body=None, **kwargs):
    add_token()
    responses.post(GAMES_URL, json=[GRAN_TURISMO_4] if body is None else body, headers={'X-Count': '24'})
    return client.search(query, platform_ids, **kwargs)


def sent_query():
    return responses.calls[-1].request.body.decode()


@responses.activate
def test_search_maps_igdb_game_to_our_fields(client):
    games, total = search(client)
    assert total == 24
    assert games == [{
        'igdb_id': 1601,
        'title': 'Gran Turismo 4',
        'cover_url': 'https://images.igdb.com/igdb/image/upload/t_cover_big/co1abc.jpg',
        'release_year': 2004,
        'genres': ['Racing', 'Simulator'],
        'summary': 'Racing simulator.',
        'releases': [{'platform_igdb_id': 8, 'release_year': 2004}],
    }]


@responses.activate
def test_search_query_limits_platforms_game_types_and_page(client):
    search(client, platform_ids=['8', 7], limit=20, offset=40)
    query = sent_query()
    assert 'search "gran turismo";' in query
    assert 'where platforms = (7,8) & game_type = (0,4,8,9,10,11);' in query
    assert 'limit 20; offset 40;' in query


@responses.activate
@pytest.mark.parametrize('query, cleaned', [
    ('zelda"; fields *; where id = 1; "', 'zelda ; fields *; where id = 1;'),
    ('a\\" b', 'a b'),
    ('  super   mario  ', 'super mario'),
])
def test_quotes_cannot_break_out_of_search_text(client, query, cleaned):
    search(client, query=query)
    assert sent_query().startswith(f'search "{cleaned}"; fields ')


@responses.activate
def test_search_handles_missing_optional_fields(client):
    game = {'id': 2, 'name': 'Neznana igra', 'platforms': [7]}
    games, _ = search(client, body=[game])
    assert games == [{
        'igdb_id': 2, 'title': 'Neznana igra', 'cover_url': '', 'release_year': None,
        'genres': [], 'summary': '', 'releases': [{'platform_igdb_id': 7, 'release_year': None}],
    }]


@responses.activate
def test_search_without_platforms_makes_no_request(client):
    assert client.search('zelda', []) == ([], 0)
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.parametrize('status', [429, 500, 503])
def test_search_errors_raise_igdb_error(client, status):
    add_token()
    responses.post(GAMES_URL, status=status)
    with pytest.raises(IGDBError):
        client.search('zelda', [7])


@responses.activate
@pytest.mark.parametrize('body', ['ni json', '[{"name": "brez id"}]'])
def test_unexpected_response_raises_igdb_error(client, body):
    add_token()
    responses.post(GAMES_URL, body=body, content_type='application/json')
    with pytest.raises(IGDBError):
        client.search('zelda', [7])
