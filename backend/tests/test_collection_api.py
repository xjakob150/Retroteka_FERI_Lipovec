from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from collection.models import Collection, CollectionItem, Condition, Region
from games import search
from games.models import Game, Platform

User = get_user_model()

pytestmark = pytest.mark.django_db

URL = '/api/collections/'


def make_user(username='marko', role=User.Role.COLLECTOR):
    return User.objects.create_user(username, f'{username}@example.com', 'dolgo-geslo-1', role=role)


def client_for(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
    return client


def create(owner, **data):
    return client_for(owner).post(URL, data, format='json')


def test_url_name():
    assert reverse('collection-list') == URL


def test_collector_creates_private_collection():
    user = make_user()
    response = create(user, name='PS2', description='Moje igre')
    assert response.status_code == 201
    collection = Collection.objects.get()
    assert collection.user == user
    assert response.data == {
        'id': collection.id,
        'name': 'PS2',
        'description': 'Moje igre',
        'is_public': False,
        'is_hidden': False,
        'created_at': response.data['created_at'],
    }


def test_collection_is_public_when_selected():
    response = create(make_user(), name='For sale', is_public=True)
    assert response.status_code == 201
    assert response.data['is_public'] is True


def test_owner_comes_from_login_not_request():
    user, other = make_user(), make_user('ana')
    create(user, name='PS2', user=other.id, is_hidden=True)
    collection = Collection.objects.get()
    assert (collection.user, collection.is_hidden) == (user, False)


def test_duplicate_name_is_rejected_with_message():
    user = make_user()
    create(user, name='PS2')
    response = create(user, name='ps2')
    assert response.status_code == 400
    assert response.data == {'name': ['You already have a collection with this name']}


def test_invalid_name_is_rejected():
    response = create(make_user(), name='')
    assert response.status_code == 400
    assert 'name' in response.data
    assert not Collection.objects.exists()


@pytest.mark.parametrize('role', [User.Role.MODERATOR, User.Role.ADMIN])
def test_moderator_and_admin_can_create_own_collection(role):
    assert create(make_user(role=role), name='PS2').status_code == 201


def test_guest_cannot_create_collection():
    response = APIClient().post(URL, {'name': 'PS2'}, format='json')
    assert response.status_code == 401
    assert not Collection.objects.exists()


def test_blocked_user_cannot_create_collection():
    user = make_user()
    client = client_for(user)
    user.is_active = False
    user.save()
    assert client.post(URL, {'name': 'PS2'}, format='json').status_code == 401


@pytest.fixture
def ps2():
    return Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)


def add_item(collection, platform, title, cover='', igdb_id=None):
    game, _ = Game.objects.get_or_create(
        title=title,
        defaults={'igdb_id': igdb_id or abs(hash(title)) % 10**8, 'cover_url': cover, 'synced_at': timezone.now()},
    )
    return CollectionItem.objects.create(
        collection=collection, game=game, platform=platform, region=Region.PAL, condition=Condition.CIB,
    )


@pytest.fixture
def igdb_fails(monkeypatch):
    def fail():
        raise AssertionError('Collection endpoints must never call IGDB')
    monkeypatch.setattr(search, 'get_client', fail)


def list_collections(user):
    return client_for(user).get(URL)


def test_list_shows_only_my_collections_oldest_first():
    user = make_user()
    Collection.objects.create(user=make_user('ana'), name='Tuja')
    for name in ['Main shelf', 'PS1', 'For sale']:
        Collection.objects.create(user=user, name=name)
    response = list_collections(user)
    assert response.status_code == 200
    assert [collection['name'] for collection in response.data] == ['Main shelf', 'PS1', 'For sale']


def test_list_item_fields_count_and_visibility(ps2):
    user = make_user()
    collection = Collection.objects.create(user=user, name='PS2', is_public=True)
    add_item(collection, ps2, 'Gran Turismo 4', 'https://images.igdb.com/gt4.jpg')
    [data] = list_collections(user).data
    assert data == {
        'id': collection.id, 'name': 'PS2', 'description': '', 'is_public': True, 'is_hidden': False,
        'created_at': data['created_at'], 'item_count': 1, 'covers': ['https://images.igdb.com/gt4.jpg'],
    }


def test_covers_are_first_five_items_by_title_with_repeats(ps2):
    collection = Collection.objects.create(user=make_user(), name='PS2')
    for title in ['Zone of the Enders', 'Burnout 3', 'Ace Combat 4', 'Gran Turismo 4', 'Gran Turismo 4', 'Okami']:
        add_item(collection, ps2, title, f'https://images.igdb.com/{title}.jpg')
    [data] = list_collections(collection.user).data
    assert data['item_count'] == 6
    assert data['covers'] == [f'https://images.igdb.com/{title}.jpg' for title in [
        'Ace Combat 4', 'Burnout 3', 'Gran Turismo 4', 'Gran Turismo 4', 'Okami',
    ]]


def test_item_without_cover_keeps_its_place(ps2):
    collection = Collection.objects.create(user=make_user(), name='PS2')
    add_item(collection, ps2, 'Brez naslovnice')
    assert list_collections(collection.user).data[0]['covers'] == ['']


def test_empty_collection_has_no_items_or_covers():
    user = make_user()
    Collection.objects.create(user=user, name='Prazna')
    [data] = list_collections(user).data
    assert (data['item_count'], data['covers']) == (0, [])


def test_user_without_collections_gets_empty_list():
    assert list_collections(make_user()).data == []


def test_guest_cannot_list_collections():
    assert APIClient().get(URL).status_code == 401


def test_list_never_calls_igdb(ps2, igdb_fails):
    collection = Collection.objects.create(user=make_user(), name='PS2')
    add_item(collection, ps2, 'Gran Turismo 4')
    assert list_collections(collection.user).status_code == 200


def test_list_query_count_does_not_grow_with_collections(ps2):
    user = make_user()
    client = client_for(user)

    def queries():
        with CaptureQueriesContext(connection) as context:
            assert client.get(URL).status_code == 200
        return len(context)

    collection = Collection.objects.create(user=user, name='Prva')
    add_item(collection, ps2, 'Igra 1')
    one = queries()
    for n in range(2, 6):
        collection = Collection.objects.create(user=user, name=f'Zbirka {n}')
        add_item(collection, ps2, f'Igra {n}')
    assert queries() == one


def detail_url(collection_id):
    return f'{URL}{collection_id}/'


def test_detail_url_name():
    assert reverse('collection-detail', args=[5]) == detail_url(5)


def test_detail_lists_items_sorted_by_title(ps2):
    collection = Collection.objects.create(user=make_user(), name='PS2', description='Opis')
    gt4 = add_item(collection, ps2, 'Gran Turismo 4', 'https://images.igdb.com/gt4.jpg')
    gt4.purchase_price = Decimal('12.50')
    gt4.save()
    add_item(collection, ps2, 'Ace Combat 4')
    response = client_for(collection.user).get(detail_url(collection.id))
    assert response.status_code == 200
    assert (response.data['name'], response.data['description'], response.data['item_count']) == ('PS2', 'Opis', 2)
    assert [item['game']['title'] for item in response.data['items']] == ['Ace Combat 4', 'Gran Turismo 4']
    assert response.data['items'][1] == {
        'id': gt4.id,
        'game': {'id': gt4.game.id, 'title': 'Gran Turismo 4', 'cover_url': 'https://images.igdb.com/gt4.jpg'},
        'platform': {'id': ps2.id, 'name': 'PlayStation 2', 'abbreviation': 'PS2'},
        'region': 'pal',
        'region_label': 'PAL',
        'condition': 'cib',
        'condition_label': 'Complete in box',
        'purchase_price': '12.50',
    }


def test_same_game_twice_is_listed_twice(ps2):
    collection = Collection.objects.create(user=make_user(), name='PS2')
    add_item(collection, ps2, 'Gran Turismo 4')
    add_item(collection, ps2, 'Gran Turismo 4')
    assert len(client_for(collection.user).get(detail_url(collection.id)).data['items']) == 2


def test_empty_collection_detail():
    collection = Collection.objects.create(user=make_user(), name='Prazna')
    data = client_for(collection.user).get(detail_url(collection.id)).data
    assert (data['item_count'], data['items']) == (0, [])


@pytest.mark.parametrize('role', [User.Role.COLLECTOR, User.Role.MODERATOR, User.Role.ADMIN])
def test_other_users_collection_is_not_found(role):
    collection = Collection.objects.create(user=make_user('ana'), name='PS2', is_public=True)
    assert client_for(make_user(role=role)).get(detail_url(collection.id)).status_code == 404


def test_missing_collection_is_not_found():
    assert client_for(make_user()).get(detail_url(99999)).status_code == 404


def test_guest_cannot_open_collection():
    collection = Collection.objects.create(user=make_user(), name='PS2')
    assert APIClient().get(detail_url(collection.id)).status_code == 401


def test_detail_never_calls_igdb(ps2, igdb_fails):
    collection = Collection.objects.create(user=make_user(), name='PS2')
    add_item(collection, ps2, 'Gran Turismo 4')
    assert client_for(collection.user).get(detail_url(collection.id)).status_code == 200


def test_detail_query_count_does_not_grow_with_items(ps2):
    collection = Collection.objects.create(user=make_user(), name='PS2')
    client = client_for(collection.user)

    def queries():
        with CaptureQueriesContext(connection) as context:
            assert client.get(detail_url(collection.id)).status_code == 200
        return len(context)

    add_item(collection, ps2, 'Igra 1')
    one = queries()
    for n in range(2, 8):
        add_item(collection, ps2, f'Igra {n}')
    assert queries() == one


def patch(user, collection_id, **data):
    return client_for(user).patch(detail_url(collection_id), data, format='json')


def delete(user, collection_id):
    return client_for(user).delete(detail_url(collection_id))


def test_owner_edits_name_description_and_visibility():
    collection = Collection.objects.create(user=make_user(), name='PS2')
    response = patch(collection.user, collection.id, name='PlayStation 2', description='Opis', is_public=True)
    assert response.status_code == 200
    assert (response.data['name'], response.data['description'], response.data['is_public']) == (
        'PlayStation 2', 'Opis', True,
    )
    collection.refresh_from_db()
    assert (collection.name, collection.is_public) == ('PlayStation 2', True)


def test_edit_with_one_field_keeps_the_others():
    collection = Collection.objects.create(user=make_user(), name='PS2', description='Opis', is_public=True)
    patch(collection.user, collection.id, name='PS2 igre')
    collection.refresh_from_db()
    assert (collection.name, collection.description, collection.is_public) == ('PS2 igre', 'Opis', True)


def test_edit_rejects_duplicate_name():
    user = make_user()
    Collection.objects.create(user=user, name='PS1')
    collection = Collection.objects.create(user=user, name='PS2')
    response = patch(user, collection.id, name='ps1')
    assert response.status_code == 400
    assert response.data == {'name': ['You already have a collection with this name']}


def test_owner_cannot_republish_hidden_collection():
    collection = Collection.objects.create(
        user=make_user(), name='Junk box', is_public=False, is_hidden=True, hidden_at=timezone.now(),
    )
    response = patch(collection.user, collection.id, is_public=True)
    assert response.status_code == 400
    assert response.data == {'is_public': ['A collection hidden by a moderator cannot be made public.']}
    collection.refresh_from_db()
    assert collection.is_public is False


def test_put_is_not_allowed():
    collection = Collection.objects.create(user=make_user(), name='PS2')
    response = client_for(collection.user).put(detail_url(collection.id), {'name': 'X'}, format='json')
    assert response.status_code == 405


def test_owner_deletes_collection_with_its_items(ps2):
    collection = Collection.objects.create(user=make_user(), name='PS2')
    for title in ['Gran Turismo 4', 'Okami']:
        add_item(collection, ps2, title)
    assert delete(collection.user, collection.id).status_code == 204
    assert not Collection.objects.filter(pk=collection.pk).exists()
    assert not CollectionItem.objects.exists()
    assert Game.objects.count() == 2


def test_owner_can_delete_hidden_collection():
    collection = Collection.objects.create(user=make_user(), name='Junk box', is_hidden=True, hidden_at=timezone.now())
    assert delete(collection.user, collection.id).status_code == 204


@pytest.mark.parametrize('role', [User.Role.COLLECTOR, User.Role.MODERATOR, User.Role.ADMIN])
def test_other_users_cannot_edit_or_delete(ps2, role):
    collection = Collection.objects.create(user=make_user('ana'), name='PS2', is_public=True)
    add_item(collection, ps2, 'Okami')
    other = make_user(role=role)
    assert patch(other, collection.id, name='Ukradeno').status_code == 404
    assert delete(other, collection.id).status_code == 404
    collection.refresh_from_db()
    assert collection.name == 'PS2'
    assert collection.items.count() == 1


def test_guest_cannot_edit_or_delete():
    collection = Collection.objects.create(user=make_user(), name='PS2')
    assert APIClient().patch(detail_url(collection.id), {'name': 'X'}, format='json').status_code == 401
    assert APIClient().delete(detail_url(collection.id)).status_code == 401
    assert Collection.objects.get(pk=collection.pk).name == 'PS2'
