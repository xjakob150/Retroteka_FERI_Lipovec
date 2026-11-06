from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from collection.models import Collection, CollectionItem
from games.models import Game, Platform

User = get_user_model()

pytestmark = pytest.mark.django_db


def make_user(username, role=User.Role.COLLECTOR):
    return User.objects.create_user(username, f'{username}@example.com', 'dolgo-geslo-1', role=role)


def client_for(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user)
    return client


def hide(user, collection):
    return client_for(user).post(reverse('public-collection-hide', args=[collection.id]))


def unhide(user, collection):
    return client_for(user).post(reverse('public-collection-unhide', args=[collection.id]))


@pytest.fixture
def owner():
    return make_user('marko')


@pytest.fixture
def collection(owner):
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    collection = Collection.objects.create(user=owner, name='Žaljivo ime', is_public=True)
    game = Game.objects.create(igdb_id=1, title='Okami', synced_at=timezone.now())
    CollectionItem.objects.create(collection=collection, game=game, platform=ps2, region='pal', condition='cib')
    return collection


def test_urls():
    assert reverse('public-collection-hide', args=[3]) == '/api/public/collections/3/hide/'
    assert reverse('public-collection-unhide', args=[3]) == '/api/public/collections/3/unhide/'


@pytest.mark.parametrize('role', [User.Role.MODERATOR, User.Role.ADMIN])
def test_moderator_hides_public_collection_and_who_and_when_are_recorded(collection, role):
    moderator = make_user('ana', role)
    response = hide(moderator, collection)
    assert response.status_code == 200
    assert (response.data['is_hidden'], response.data['item_count']) == (True, 1)
    collection.refresh_from_db()
    assert (collection.is_hidden, collection.hidden_by) == (True, moderator)
    assert timezone.now() - collection.hidden_at < timedelta(seconds=5)
    assert collection.items.count() == 1


def test_hidden_collection_disappears_for_others_but_owner_still_has_it(collection, owner):
    hide(make_user('ana', User.Role.MODERATOR), collection)
    assert client_for().get('/api/public/collections/').data['results'] == []
    assert client_for().get(f'/api/public/collections/{collection.id}/').status_code == 404
    mine = client_for(owner).get('/api/collections/').data
    assert [(entry['name'], entry['is_hidden']) for entry in mine] == [('Žaljivo ime', True)]


def test_owner_cannot_republish_after_making_hidden_collection_private(collection, owner):
    hide(make_user('ana', User.Role.MODERATOR), collection)
    assert client_for(owner).patch(f'/api/collections/{collection.id}/', {'is_public': False}, format='json').status_code == 200
    response = client_for(owner).patch(f'/api/collections/{collection.id}/', {'is_public': True}, format='json')
    assert response.status_code == 400


def test_hiding_twice_is_rejected_and_keeps_first_moderator(collection):
    first, second = make_user('ana', User.Role.MODERATOR), make_user('bojan', User.Role.MODERATOR)
    hide(first, collection)
    response = hide(second, collection)
    assert response.status_code == 400
    assert response.data == {'detail': 'This collection is already hidden.'}
    collection.refresh_from_db()
    assert collection.hidden_by == first


def test_moderator_unhides_collection(collection):
    hide(make_user('ana', User.Role.MODERATOR), collection)
    response = unhide(make_user('bojan', User.Role.MODERATOR), collection)
    assert response.status_code == 200
    assert response.data['is_hidden'] is False
    collection.refresh_from_db()
    assert (collection.is_hidden, collection.hidden_by, collection.hidden_at) == (False, None, None)
    assert client_for().get(f'/api/public/collections/{collection.id}/').status_code == 200


def test_unhiding_hidden_private_collection_lets_owner_publish_again(collection, owner):
    hide(make_user('ana', User.Role.MODERATOR), collection)
    client_for(owner).patch(f'/api/collections/{collection.id}/', {'is_public': False}, format='json')
    assert unhide(make_user('bojan', User.Role.MODERATOR), collection).status_code == 200
    response = client_for(owner).patch(f'/api/collections/{collection.id}/', {'is_public': True}, format='json')
    assert response.status_code == 200


def test_unhiding_visible_collection_is_rejected(collection):
    response = unhide(make_user('ana', User.Role.MODERATOR), collection)
    assert response.status_code == 400
    assert response.data == {'detail': 'This collection is not hidden.'}


@pytest.mark.parametrize('role', [User.Role.MODERATOR, User.Role.ADMIN])
def test_moderator_can_hide_own_collection_but_not_unhide_it(role):
    moderator = make_user('ana', role)
    own = Collection.objects.create(user=moderator, name='Moja', is_public=True)
    assert hide(moderator, own).status_code == 200
    assert unhide(moderator, own).status_code == 403
    own.refresh_from_db()
    assert own.is_hidden is True


def test_collector_cannot_hide_or_unhide(collection, owner):
    collector = make_user('obiskovalec')
    assert hide(collector, collection).status_code == 403
    assert hide(owner, collection).status_code == 403
    Collection.objects.filter(pk=collection.pk).update(is_hidden=True)
    assert unhide(collector, collection).status_code == 403
    assert unhide(owner, collection).status_code == 403


def test_guest_cannot_hide_or_unhide(collection):
    assert hide(None, collection).status_code == 401
    assert unhide(None, collection).status_code == 401
    collection.refresh_from_db()
    assert collection.is_hidden is False


def test_private_collection_cannot_be_hidden(owner):
    private = Collection.objects.create(user=owner, name='Zasebna')
    response = hide(make_user('ana', User.Role.MODERATOR), private)
    assert response.status_code == 404
    assert response.data == {'detail': 'Collection not found'}
    private.refresh_from_db()
    assert private.is_hidden is False


def test_get_on_actions_is_not_allowed(collection):
    moderator = make_user('ana', User.Role.MODERATOR)
    assert client_for(moderator).get(reverse('public-collection-hide', args=[collection.id])).status_code == 405
