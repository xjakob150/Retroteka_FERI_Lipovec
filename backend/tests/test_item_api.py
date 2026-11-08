from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from collection.models import Collection, CollectionItem
from games import search
from games.models import Game, GameRelease, Platform
from pricing.services import record_price_check

User = get_user_model()

pytestmark = pytest.mark.django_db

URL = '/api/items/'


def make_user(username='marko'):
    return User.objects.create_user(username, f'{username}@example.com', 'dolgo-geslo-1')


def client_for(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
    return client


@pytest.fixture
def owner():
    return make_user()


@pytest.fixture
def payload(owner):
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    game = Game.objects.create(
        igdb_id=1601, title='Gran Turismo 4', cover_url='https://images.igdb.com/gt4.jpg', synced_at=timezone.now(),
    )
    GameRelease.objects.create(game=game, platform=ps2, release_year=2004)
    collection = Collection.objects.create(user=owner, name='PS2')
    return {
        'collection': collection.id, 'game': game.id, 'platform': ps2.id,
        'region': 'pal', 'condition': 'cib', 'purchase_price': '12.50', 'notes': 'Sejem v Ljubljani',
    }


def add(user, data):
    return client_for(user).post(URL, data, format='json')


def test_url_name():
    assert reverse('item-list') == URL


def test_owner_adds_item_and_gets_it_back(owner, payload):
    response = add(owner, payload)
    assert response.status_code == 201
    item = CollectionItem.objects.get()
    assert response.data == {
        'id': item.id,
        'collection': payload['collection'],
        'game': {'id': payload['game'], 'title': 'Gran Turismo 4', 'cover_url': 'https://images.igdb.com/gt4.jpg'},
        'platform': {'id': payload['platform'], 'name': 'PlayStation 2', 'abbreviation': 'PS2'},
        'region': 'pal',
        'region_label': 'PAL',
        'condition': 'cib',
        'condition_label': 'Complete in box',
        'purchase_price': '12.50',
        'notes': 'Sejem v Ljubljani',
        'estimated_price': None,
        'price_checked_at': None,
        'created_at': response.data['created_at'],
    }


def test_item_appears_in_collection(owner, payload):
    add(owner, payload)
    data = client_for(owner).get(f"/api/collections/{payload['collection']}/").data
    assert data['item_count'] == 1
    assert data['items'][0]['game']['title'] == 'Gran Turismo 4'


def test_same_game_twice_makes_two_items(owner, payload):
    assert add(owner, payload).status_code == 201
    assert add(owner, payload).status_code == 201
    assert CollectionItem.objects.count() == 2


def test_missing_region_is_reported(owner, payload):
    del payload['region']
    response = add(owner, payload)
    assert response.status_code == 400
    assert response.data == {'region': ['Region is required']}


def test_item_cannot_be_added_to_other_users_collection(owner, payload):
    foreign = Collection.objects.create(user=make_user('ana'), name='Tuja')
    response = add(owner, {**payload, 'collection': foreign.id})
    assert response.status_code == 400
    assert response.data == {'collection': ['Select one of your collections.']}
    assert not CollectionItem.objects.exists()


def test_guest_cannot_add_item(payload):
    assert APIClient().post(URL, payload, format='json').status_code == 401
    assert not CollectionItem.objects.exists()


def test_adding_item_never_calls_igdb(owner, payload, monkeypatch):
    def fail():
        raise AssertionError('Item endpoints must never call IGDB')
    monkeypatch.setattr(search, 'get_client', fail)
    assert add(owner, payload).status_code == 201


def test_listing_items_is_not_available(owner):
    assert client_for(owner).get(URL).status_code == 405


@pytest.fixture
def item(owner, payload):
    return CollectionItem.objects.get(pk=add(owner, payload).data['id'])


def detail_url(item_id):
    return f'{URL}{item_id}/'


def test_detail_url_name():
    assert reverse('item-detail', args=[3]) == detail_url(3)


def test_owner_opens_item_with_game_details(owner, item):
    item.game.genres, item.game.summary, item.game.release_year = ['Racing'], 'Dirkalna igra.', 2004
    item.game.save()
    response = client_for(owner).get(detail_url(item.id))
    assert response.status_code == 200
    assert response.data['game'] == {
        'id': item.game.id, 'title': 'Gran Turismo 4', 'cover_url': 'https://images.igdb.com/gt4.jpg',
        'release_year': 2004, 'genres': ['Racing'], 'summary': 'Dirkalna igra.',
        'platforms': [{'id': item.platform.id, 'name': 'PlayStation 2', 'abbreviation': 'PS2', 'release_year': 2004}],
    }
    assert (response.data['notes'], response.data['purchase_price']) == ('Sejem v Ljubljani', '12.50')


def test_owner_edits_item(owner, item):
    response = client_for(owner).patch(detail_url(item.id), {'condition': 'new', 'notes': ''}, format='json')
    assert response.status_code == 200
    assert (response.data['condition'], response.data['condition_label'], response.data['notes']) == (
        'new', 'New / sealed', '',
    )
    assert 'platforms' in response.data['game']


def test_owner_moves_item(owner, item):
    for_sale = Collection.objects.create(user=owner, name='For sale')
    response = client_for(owner).patch(detail_url(item.id), {'collection': for_sale.id}, format='json')
    assert response.status_code == 200
    assert response.data['collection'] == for_sale.id
    data = client_for(owner).get(f'/api/collections/{for_sale.id}/').data
    assert [entry['id'] for entry in data['items']] == [item.id]


def test_invalid_edit_is_rejected_and_nothing_changes(owner, item):
    response = client_for(owner).patch(detail_url(item.id), {'purchase_price': '-1'}, format='json')
    assert response.status_code == 400
    item.refresh_from_db()
    assert f'{item.purchase_price}' == '12.50'


def test_owner_removes_item(owner, item):
    collection_id = item.collection_id
    assert client_for(owner).delete(detail_url(item.id)).status_code == 204
    assert not CollectionItem.objects.exists()
    assert Collection.objects.filter(pk=collection_id).exists()
    assert Game.objects.exists()


def test_put_is_not_allowed(owner, item):
    assert client_for(owner).put(detail_url(item.id), {'region': 'pal'}, format='json').status_code == 405


@pytest.mark.parametrize('role', [User.Role.COLLECTOR, User.Role.MODERATOR, User.Role.ADMIN])
def test_other_users_cannot_open_edit_move_or_remove(item, role):
    other = User.objects.create_user('ana', 'ana@example.com', 'dolgo-geslo-1', role=role)
    own = Collection.objects.create(user=other, name='Moja')
    client = client_for(other)
    assert client.get(detail_url(item.id)).status_code == 404
    assert client.patch(detail_url(item.id), {'notes': 'Ukradeno'}, format='json').status_code == 404
    assert client.patch(detail_url(item.id), {'collection': own.id}, format='json').status_code == 404
    assert client.delete(detail_url(item.id)).status_code == 404
    item.refresh_from_db()
    assert (item.notes, item.collection.user.username) == ('Sejem v Ljubljani', 'marko')


def test_guest_cannot_open_or_change_item(item):
    assert APIClient().get(detail_url(item.id)).status_code == 401
    assert APIClient().delete(detail_url(item.id)).status_code == 401
    assert CollectionItem.objects.filter(pk=item.pk).exists()


def test_item_endpoints_never_call_igdb(owner, item, monkeypatch):
    def fail():
        raise AssertionError('Item endpoints must never call IGDB')
    monkeypatch.setattr(search, 'get_client', fail)
    client = client_for(owner)
    assert client.get(detail_url(item.id)).status_code == 200
    assert client.patch(detail_url(item.id), {'notes': 'x'}, format='json').status_code == 200
    assert client.delete(detail_url(item.id)).status_code == 204


@pytest.fixture
def priced_item(owner, item):
    record_price_check(item, '15.40', 21)
    record_price_check(item, '18.50', 23)
    return item


@pytest.mark.parametrize('changes', [
    {'region': 'ntsc_j'},
    {'condition': 'loose'},
    {'platform': 'n64'},
])
def test_changing_edition_deletes_price_history(owner, priced_item, changes):
    if changes.get('platform') == 'n64':
        n64 = Platform.objects.create(igdb_id=4, name='Nintendo 64', abbreviation='N64', is_supported=True)
        GameRelease.objects.create(game=priced_item.game, platform=n64)
        changes = {'platform': n64.id}
    response = client_for(owner).patch(detail_url(priced_item.id), changes, format='json')
    assert response.status_code == 200
    assert (response.data['estimated_price'], response.data['price_checked_at']) == (None, None)
    priced_item.refresh_from_db()
    assert priced_item.price_checks.count() == 0
    assert (priced_item.estimated_price, priced_item.price_checked_at) == (None, None)


@pytest.mark.parametrize('changes', [
    {'notes': 'Nove opombe'},
    {'purchase_price': '20.00'},
    {'region': 'pal', 'condition': 'cib'},
])
def test_other_changes_keep_price_history(owner, priced_item, changes):
    assert client_for(owner).patch(detail_url(priced_item.id), changes, format='json').status_code == 200
    priced_item.refresh_from_db()
    assert priced_item.price_checks.count() == 2
    assert f'{priced_item.estimated_price}' == '18.50'


def test_moving_item_keeps_price_history(owner, priced_item):
    for_sale = Collection.objects.create(user=owner, name='For sale')
    client_for(owner).patch(detail_url(priced_item.id), {'collection': for_sale.id}, format='json')
    priced_item.refresh_from_db()
    assert priced_item.price_checks.count() == 2


def test_invalid_edition_change_keeps_price_history(owner, priced_item):
    response = client_for(owner).patch(detail_url(priced_item.id), {'region': 'ntsc_j', 'purchase_price': '-1'}, format='json')
    assert response.status_code == 400
    priced_item.refresh_from_db()
    assert (priced_item.region, priced_item.price_checks.count()) == ('pal', 2)


def test_new_item_gets_price_from_ebay(owner, payload, ebay):
    fake = ebay(result=(Decimal('18.50'), 23))
    response = add(owner, payload)
    assert response.status_code == 201
    assert response.data['estimated_price'] == '18.50'
    assert response.data['price_checked_at'] is not None
    item = CollectionItem.objects.get()
    assert fake.calls == [item]
    [check] = item.price_checks.all()
    assert (check.price, check.listing_count, check.source) == (Decimal('18.50'), 23, 'ebay')


def test_ebay_failure_still_saves_item_without_price(owner, payload):
    response = add(owner, payload)
    assert response.status_code == 201
    assert (response.data['estimated_price'], response.data['price_checked_at']) == (None, None)
    item = CollectionItem.objects.get()
    assert item.price_checks.count() == 0


def test_no_listings_saves_price_not_available(owner, payload, ebay):
    ebay(result=(None, 0))
    response = add(owner, payload)
    assert response.data['estimated_price'] is None
    assert response.data['price_checked_at'] is not None
    assert CollectionItem.objects.get().price_checks.get().listing_count == 0


def test_invalid_item_does_not_call_ebay(owner, payload, ebay):
    fake = ebay(result=(Decimal('18.50'), 23))
    del payload['region']
    assert add(owner, payload).status_code == 400
    assert fake.calls == []


def test_edition_change_fetches_new_price(owner, priced_item, ebay):
    fake = ebay(result=(Decimal('9.90'), 7))
    response = client_for(owner).patch(detail_url(priced_item.id), {'condition': 'loose'}, format='json')
    assert response.status_code == 200
    assert response.data['estimated_price'] == '9.90'
    priced_item.refresh_from_db()
    assert [check.price for check in priced_item.price_checks.all()] == [Decimal('9.90')]
    assert fake.calls == [priced_item]


def test_edition_change_with_ebay_down_leaves_item_without_price(owner, priced_item):
    response = client_for(owner).patch(detail_url(priced_item.id), {'region': 'ntsc_j'}, format='json')
    assert response.status_code == 200
    assert response.data['estimated_price'] is None
    priced_item.refresh_from_db()
    assert (priced_item.region, priced_item.price_checks.count()) == ('ntsc_j', 0)


@pytest.mark.parametrize('changes', [{'notes': 'Nove opombe'}, {'region': 'pal', 'condition': 'cib'}])
def test_other_changes_do_not_call_ebay(owner, priced_item, ebay, changes):
    fake = ebay(result=(Decimal('9.90'), 7))
    client_for(owner).patch(detail_url(priced_item.id), changes, format='json')
    assert fake.calls == []
