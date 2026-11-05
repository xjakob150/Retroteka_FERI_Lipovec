import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from collection.models import Collection, CollectionItem
from games import search
from games.models import Game, GameRelease, Platform

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
