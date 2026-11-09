from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from collection.models import Collection, CollectionItem
from games import search
from games.models import Game, Platform

User = get_user_model()

pytestmark = pytest.mark.django_db

URL = '/api/public/collections/'


def make_user(username, role=User.Role.COLLECTOR, **fields):
    return User.objects.create_user(username, f'{username}@example.com', 'dolgo-geslo-1', role=role, **fields)


def client_for(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    return client


def names(response):
    return [collection['name'] for collection in response.data['results']]


@pytest.fixture
def owner():
    return make_user('marko')


@pytest.fixture
def collections(owner):
    hidden_by = make_user('ana', User.Role.MODERATOR)
    return {
        'public': Collection.objects.create(user=owner, name='Javna', is_public=True),
        'private': Collection.objects.create(user=owner, name='Zasebna'),
        'hidden': Collection.objects.create(
            user=owner, name='Skrita', is_public=True, is_hidden=True, hidden_by=hidden_by, hidden_at=timezone.now(),
        ),
        'blocked': Collection.objects.create(user=make_user('blokiran', is_active=False), name='Blokirana', is_public=True),
    }


def test_url_names():
    assert reverse('public-collection-list') == URL
    assert reverse('public-collection-detail', args=[4]) == f'{URL}4/'


@pytest.mark.parametrize('viewer', [None, 'collector', 'owner'])
def test_guests_and_collectors_see_only_visible_public_collections(collections, owner, viewer):
    user = {None: None, 'collector': make_user('obiskovalec'), 'owner': owner}[viewer]
    response = client_for(user).get(URL)
    assert response.status_code == 200
    assert names(response) == ['Javna']
    assert response.data['count'] == 1


@pytest.mark.parametrize('role', [User.Role.MODERATOR, User.Role.ADMIN])
def test_moderators_also_see_hidden_public_collections(collections, role):
    response = client_for(make_user('mod', role)).get(URL)
    assert sorted(names(response)) == ['Javna', 'Skrita']
    hidden = next(entry for entry in response.data['results'] if entry['name'] == 'Skrita')
    assert hidden['is_hidden'] is True


def test_list_entry_has_owner_and_item_count(owner):
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    game = Game.objects.create(igdb_id=1, title='Okami', synced_at=timezone.now())
    collection = Collection.objects.create(user=owner, name='Javna', is_public=True)
    for _ in range(2):
        CollectionItem.objects.create(collection=collection, game=game, platform=ps2, region='pal', condition='cib')
    [entry] = client_for().get(URL).data['results']
    assert (entry['owner'], entry['item_count']) == ('marko', 2)


def test_newest_first_and_20_per_page(owner):
    for n in range(25):
        Collection.objects.create(user=owner, name=f'Zbirka {n:02}', is_public=True)
    first = client_for().get(URL)
    assert first.data['count'] == 25
    assert names(first)[:2] == ['Zbirka 24', 'Zbirka 23']
    assert len(names(first)) == 20
    second = client_for().get(URL, {'page': 2})
    assert names(second) == [f'Zbirka {n:02}' for n in range(4, -1, -1)]
    assert client_for().get(URL, {'page': 5}).data['results'] == []


@pytest.mark.parametrize('page', ['0', 'abc'])
def test_invalid_page_is_rejected(page):
    assert client_for().get(URL, {'page': page}).status_code == 400


@pytest.fixture
def public_with_item(owner):
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    collection = Collection.objects.create(user=owner, name='Javna', is_public=True)
    for title in ['Okami', 'Gran Turismo 4']:
        game = Game.objects.create(igdb_id=abs(hash(title)) % 10**8, title=title, synced_at=timezone.now())
        CollectionItem.objects.create(
            collection=collection, game=game, platform=ps2, region='pal', condition='cib',
            purchase_price=Decimal('12.00'), notes='Skrivna opomba',
        )
    return collection


def test_guest_opens_public_collection_without_prices_or_notes(public_with_item):
    response = client_for().get(f'{URL}{public_with_item.id}/')
    assert response.status_code == 200
    assert (response.data['owner'], response.data['item_count']) == ('marko', 2)
    assert [item['game']['title'] for item in response.data['items']] == ['Gran Turismo 4', 'Okami']
    for item in response.data['items']:
        assert 'purchase_price' not in item and 'notes' not in item and 'can_refresh_price' not in item
    assert b'Skrivna opomba' not in response.content
    assert b'12.00' not in response.content


@pytest.mark.parametrize('name', ['private', 'hidden', 'blocked'])
@pytest.mark.parametrize('viewer', [None, 'collector', 'owner'])
def test_invisible_collections_are_not_found(collections, owner, name, viewer):
    user = {None: None, 'collector': make_user('obiskovalec'), 'owner': owner}[viewer]
    response = client_for(user).get(f"{URL}{collections[name].id}/")
    assert response.status_code == 404
    assert response.data == {'detail': 'Collection not found'}


def test_missing_collection_is_not_found():
    assert client_for().get(f'{URL}99999/').data == {'detail': 'Collection not found'}


def test_moderator_opens_hidden_but_not_private_collection(collections):
    moderator = make_user('mod', User.Role.MODERATOR)
    assert client_for(moderator).get(f"{URL}{collections['hidden'].id}/").status_code == 200
    assert client_for(moderator).get(f"{URL}{collections['private'].id}/").status_code == 404


@pytest.mark.parametrize('method', ['post', 'patch', 'put', 'delete'])
def test_public_collections_cannot_be_changed(collections, owner, method):
    collection = collections['public']
    url = URL if method == 'post' else f'{URL}{collection.id}/'
    response = getattr(client_for(owner), method)(url, {'name': 'Spremenjeno'}, format='json')
    assert response.status_code == 405
    collection.refresh_from_db()
    assert collection.name == 'Javna'


def test_public_endpoints_never_call_igdb(public_with_item, monkeypatch):
    def fail():
        raise AssertionError('Collection endpoints must never call IGDB')
    monkeypatch.setattr(search, 'get_client', fail)
    assert client_for().get(URL).status_code == 200
    assert client_for().get(f'{URL}{public_with_item.id}/').status_code == 200


def test_list_query_count_does_not_grow(owner):
    def queries():
        with CaptureQueriesContext(connection) as context:
            assert client_for().get(URL).status_code == 200
        return len(context)

    Collection.objects.create(user=owner, name='Prva', is_public=True)
    one = queries()
    for n in range(5):
        Collection.objects.create(user=make_user(f'u{n}'), name=f'Zbirka {n}', is_public=True)
    assert queries() == one


@pytest.mark.parametrize('role', [User.Role.MODERATOR, User.Role.ADMIN])
def test_moderators_see_hidden_collection_made_private_by_owner(owner, role):
    hidden_private = Collection.objects.create(
        user=owner, name='Skrita zasebna', is_public=False, is_hidden=True, hidden_at=timezone.now(),
    )
    moderator = make_user('mod', role)
    assert 'Skrita zasebna' in names(client_for(moderator).get(URL))
    assert client_for(moderator).get(f'{URL}{hidden_private.id}/').status_code == 200
    assert client_for().get(f'{URL}{hidden_private.id}/').status_code == 404
    assert client_for(owner).get(f'{URL}{hidden_private.id}/').status_code == 404
