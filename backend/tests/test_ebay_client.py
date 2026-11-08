import base64
from decimal import Decimal
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import responses

from pricing import ebay
from pricing.ebay import SEARCH_URL, TOKEN_URL, EbayClient, EbayError, get_client


@pytest.fixture
def clock(monkeypatch):
    now = {'value': 1000.0}
    monkeypatch.setattr(ebay.time, 'monotonic', lambda: now['value'])
    return now


@pytest.fixture
def client():
    return EbayClient(client_id='id', client_secret='skrivnost')


def add_token(token='zeton', expires_in=7200):
    responses.post(TOKEN_URL, json={'access_token': token, 'expires_in': expires_in, 'token_type': 'Application Access Token'})


def token_requests():
    return [call for call in responses.calls if call.request.url.startswith(TOKEN_URL)]


@responses.activate
def test_token_uses_basic_auth_and_browse_scope(client):
    add_token()
    responses.get(SEARCH_URL, json={'total': 0})
    client.search({'q': 'okami'})
    request = token_requests()[0].request
    assert request.headers['Authorization'] == 'Basic ' + base64.b64encode(b'id:skrivnost').decode()
    assert 'grant_type=client_credentials' in request.body
    assert 'scope=https%3A%2F%2Fapi.ebay.com%2Foauth%2Fapi_scope' in request.body


@responses.activate
def test_search_sends_token_marketplace_and_params(client):
    add_token()
    responses.get(SEARCH_URL, json={'total': 0})
    assert client.search({'q': 'okami', 'limit': 50}) == {'total': 0}
    request = responses.calls[1].request
    assert request.headers['Authorization'] == 'Bearer zeton'
    assert request.headers['X-EBAY-C-MARKETPLACE-ID'] == 'EBAY_DE'
    assert 'q=okami' in request.url and 'limit=50' in request.url


@responses.activate
def test_token_is_reused_until_shortly_before_expiry(client, clock):
    add_token('prvi')
    add_token('drugi')
    responses.get(SEARCH_URL, json={})
    client.search({})
    clock['value'] += 7200 - 61
    client.search({})
    assert len(token_requests()) == 1
    clock['value'] += 2
    client.search({})
    assert len(token_requests()) == 2
    assert responses.calls[-1].request.headers['Authorization'] == 'Bearer drugi'


@responses.activate
def test_rejected_token_raises_error_without_new_token(client):
    add_token()
    responses.get(SEARCH_URL, status=401)
    with pytest.raises(EbayError):
        client.search({})
    assert len(token_requests()) == 1


@responses.activate
@pytest.mark.parametrize('status', [400, 401, 500])
def test_token_errors_raise_ebay_error(client, status):
    responses.post(TOKEN_URL, status=status)
    with pytest.raises(EbayError):
        client.search({})


@responses.activate
@pytest.mark.parametrize('client_id, client_secret', [('', 'skrivnost'), ('id', '')])
def test_missing_credentials_raise_error_without_request(client_id, client_secret):
    with pytest.raises(EbayError):
        EbayClient(client_id=client_id, client_secret=client_secret).search({})
    assert len(responses.calls) == 0


@responses.activate
@pytest.mark.parametrize('failure', [requests.ReadTimeout(), requests.ConnectionError()])
def test_timeout_or_unreachable_ebay_raises_error(client, failure):
    add_token()
    responses.get(SEARCH_URL, body=failure)
    with pytest.raises(EbayError):
        client.search({})


@responses.activate
@pytest.mark.parametrize('status', [429, 500, 503])
def test_search_errors_raise_ebay_error(client, status):
    add_token()
    responses.get(SEARCH_URL, status=status)
    with pytest.raises(EbayError):
        client.search({})


@responses.activate
def test_invalid_json_raises_ebay_error(client):
    add_token()
    responses.get(SEARCH_URL, body='ni json', content_type='application/json')
    with pytest.raises(EbayError):
        client.search({})


def test_credentials_come_from_environment(monkeypatch):
    monkeypatch.setenv('EBAY_CLIENT_ID', 'iz-okolja')
    monkeypatch.setenv('EBAY_CLIENT_SECRET', 'skrivnost-iz-okolja')
    assert (EbayClient().client_id, EbayClient().client_secret) == ('iz-okolja', 'skrivnost-iz-okolja')


def test_get_client_returns_one_shared_client():
    assert get_client() is get_client()


ITEM = SimpleNamespace(
    game=SimpleNamespace(title='Okami'),
    platform=SimpleNamespace(name='PlayStation 2', abbreviation='PS2'),
    region='pal',
    condition='cib',
)


def listings(*prices, currency='EUR'):
    return {'total': len(prices), 'itemSummaries': [{'price': {'value': p, 'currency': currency}} for p in prices]}


def price_for(client, body):
    add_token()
    responses.get(SEARCH_URL, json=body)
    return client.price_for(ITEM)


@responses.activate
def test_search_params_limit_listings_to_fixed_price_euro_games(client):
    price_for(client, listings())
    params = parse_qs(urlparse(responses.calls[-1].request.url).query)
    assert params['q'] == ['Okami (PS2, PlayStation 2) PAL (OVP, CIB, complete, Anleitung) -defekt -Konvolut -Sammlung']
    assert params['filter'] == ['buyingOptions:{FIXED_PRICE},priceCurrency:EUR']
    assert params['category_ids'] == ['139973']
    assert params['limit'] == ['50']


@responses.activate
def test_median_of_odd_number_of_listings(client):
    assert price_for(client, listings('25.00', '40.00', '32.00')) == (Decimal('32.00'), 3)


@responses.activate
def test_median_of_even_number_is_rounded_to_cents(client):
    assert price_for(client, listings('10.00', '15.25')) == (Decimal('12.63'), 2)


@responses.activate
def test_one_outlier_does_not_move_the_median(client):
    assert price_for(client, listings('30', '31', '32', '33', '999')) == (Decimal('32.00'), 5)


@responses.activate
@pytest.mark.parametrize('body', [{'total': 0}, listings()])
def test_no_listings_gives_no_price(client, body):
    assert price_for(client, body) == (None, 0)


@responses.activate
def test_listings_in_other_currency_are_left_out(client):
    body = listings('20.00', '30.00')
    body['itemSummaries'].append({'price': {'value': '5.00', 'currency': 'GBP'}})
    assert price_for(client, body) == (Decimal('25.00'), 2)


@responses.activate
@pytest.mark.parametrize('body', [
    {'itemSummaries': [{'title': 'brez cene'}]},
    {'itemSummaries': [{'price': {'value': 'abc', 'currency': 'EUR'}}]},
    {'itemSummaries': 'ni seznam'},
])
def test_unexpected_listing_raises_ebay_error(client, body):
    with pytest.raises(EbayError):
        price_for(client, body)
