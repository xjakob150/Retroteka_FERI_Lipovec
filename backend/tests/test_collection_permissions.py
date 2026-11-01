from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from collection.models import Collection, CollectionItem, Condition, Region
from collection.permissions import CanHideCollection, CanUnhideCollection, IsCollectionOwner, IsItemOwner
from games.models import Game, Platform

pytestmark = pytest.mark.django_db

ALL_PERMISSIONS = [IsCollectionOwner, IsItemOwner, CanHideCollection, CanUnhideCollection]


def make_user(username, role='collector'):
    return get_user_model().objects.create_user(
        username=username, email=f'{username}@example.com', password='geslo-za-test', role=role,
    )


def allowed(permission_class, user, obj=None):
    permission = permission_class()
    request = SimpleNamespace(user=user)
    if not permission.has_permission(request, None):
        return False
    return obj is None or permission.has_object_permission(request, None, obj)


@pytest.fixture
def owner():
    return make_user('lastnik')


@pytest.fixture
def collection(owner):
    return Collection.objects.create(user=owner, name='PS2', is_public=True)


@pytest.fixture
def item(collection):
    return CollectionItem.objects.create(
        collection=collection,
        game=Game.objects.create(igdb_id=1, title='Gran Turismo 4', synced_at=timezone.now()),
        platform=Platform.objects.create(igdb_id=8, name='PlayStation 2'),
        region=Region.PAL,
        condition=Condition.CIB,
    )


@pytest.mark.parametrize('permission_class', ALL_PERMISSIONS)
def test_guest_is_rejected(permission_class):
    assert not allowed(permission_class, AnonymousUser())


def test_owner_passes_ownership_checks(owner, collection, item):
    assert allowed(IsCollectionOwner, owner, collection)
    assert allowed(IsItemOwner, owner, item)


@pytest.mark.parametrize('role', ['collector', 'moderator', 'admin'])
def test_other_users_fail_ownership_checks_in_any_role(role, collection, item):
    other = make_user('drugi', role)
    assert not allowed(IsCollectionOwner, other, collection)
    assert not allowed(IsItemOwner, other, item)


def test_collector_cannot_hide_or_unhide(collection):
    collector = make_user('zbiralec')
    assert not allowed(CanHideCollection, collector, collection)
    assert not allowed(CanUnhideCollection, collector, collection)


@pytest.mark.parametrize('role', ['moderator', 'admin'])
def test_moderator_and_admin_can_hide_and_unhide_others_collection(role, collection):
    moderator = make_user('moderator', role)
    assert allowed(CanHideCollection, moderator, collection)
    assert allowed(CanUnhideCollection, moderator, collection)


@pytest.mark.parametrize('role', ['moderator', 'admin'])
def test_moderator_and_admin_can_hide_own_but_never_unhide_it(role):
    moderator = make_user('moderator', role)
    own = Collection.objects.create(
        user=moderator, name='PS2', is_hidden=True, hidden_by=moderator, hidden_at=timezone.now(),
    )
    assert allowed(CanHideCollection, moderator, own)
    assert not allowed(CanUnhideCollection, moderator, own)
