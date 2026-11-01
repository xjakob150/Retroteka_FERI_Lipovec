from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone

from collection.models import Collection, CollectionItem, Condition, Region
from games.models import Game, Platform

pytestmark = pytest.mark.django_db


def make_user(username='jakob'):
    return get_user_model().objects.create_user(
        username=username, email=f'{username}@example.com', password='geslo-za-test',
    )


def test_new_collection_is_private_and_not_hidden():
    collection = Collection.objects.create(user=make_user(), name='PS2')
    assert collection.is_public is False
    assert collection.is_hidden is False
    assert collection.hidden_by is None
    assert collection.hidden_at is None


def test_created_at_is_set_on_create():
    before = timezone.now()
    collection = Collection.objects.create(user=make_user(), name='PS2')
    assert before <= collection.created_at <= timezone.now()


def test_user_cannot_have_two_collections_with_same_name():
    user = make_user()
    Collection.objects.create(user=user, name='PS2')
    with pytest.raises(IntegrityError):
        Collection.objects.create(user=user, name='PS2')


@pytest.mark.parametrize('name', ['ps2', 'Ps2'])
def test_collection_name_is_unique_regardless_of_case(name):
    user = make_user()
    Collection.objects.create(user=user, name='PS2')
    with pytest.raises(IntegrityError):
        Collection.objects.create(user=user, name=name)


def test_different_users_can_use_same_collection_name():
    Collection.objects.create(user=make_user('prvi'), name='PS2')
    Collection.objects.create(user=make_user('drugi'), name='PS2')
    assert Collection.objects.filter(name='PS2').count() == 2


@pytest.mark.parametrize('fields', [
    {'name': ''},
    {'name': 'x' * 101},
    {'name': 'PS2', 'description': 'x' * 501},
])
def test_invalid_name_or_description_is_rejected(fields):
    with pytest.raises(ValidationError):
        Collection(user=make_user(), **fields).full_clean()


def test_longest_name_and_description_and_empty_description_are_valid():
    user = make_user()
    Collection(user=user, name='x' * 100, description='x' * 500).full_clean()
    Collection(user=user, name='PS2').full_clean()


def test_deleting_owner_deletes_collections():
    user = make_user()
    Collection.objects.create(user=user, name='PS2')
    user.delete()
    assert Collection.objects.count() == 0


def test_deleting_moderator_keeps_hidden_collection():
    moderator = make_user('moderator')
    collection = Collection.objects.create(
        user=make_user(), name='PS2', is_hidden=True, hidden_by=moderator, hidden_at=timezone.now(),
    )
    moderator.delete()
    collection.refresh_from_db()
    assert collection.is_hidden is True
    assert collection.hidden_by is None


@pytest.fixture
def item_fields():
    return {
        'collection': Collection.objects.create(user=make_user(), name='PS2'),
        'game': Game.objects.create(igdb_id=1, title='Gran Turismo 4', synced_at=timezone.now()),
        'platform': Platform.objects.create(igdb_id=8, name='PlayStation 2'),
        'region': Region.PAL,
        'condition': Condition.CIB,
    }


def test_region_and_condition_values_match_data_model():
    assert set(Region.values) == {'pal', 'ntsc_u', 'ntsc_j'}
    assert set(Condition.values) == {'loose', 'cib', 'new'}


def test_new_item_has_no_price_and_has_created_at(item_fields):
    item = CollectionItem.objects.create(**item_fields)
    assert item.purchase_price is None
    assert item.notes == ''
    assert item.estimated_price is None
    assert item.price_checked_at is None
    assert item.created_at is not None


def test_same_game_can_be_added_repeatedly_to_same_collection(item_fields):
    CollectionItem.objects.create(**item_fields)
    CollectionItem.objects.create(**item_fields)
    assert item_fields['collection'].items.count() == 2


@pytest.mark.parametrize('field', ['collection', 'game', 'platform', 'region', 'condition'])
def test_item_required_fields(item_fields, field):
    del item_fields[field]
    with pytest.raises(ValidationError) as error:
        CollectionItem(**item_fields).full_clean()
    assert field in error.value.message_dict


@pytest.mark.parametrize('field', ['region', 'condition'])
def test_item_rejects_unknown_choice(item_fields, field):
    item_fields[field] = 'neznano'
    with pytest.raises(ValidationError) as error:
        CollectionItem(**item_fields).full_clean()
    assert field in error.value.message_dict


@pytest.mark.parametrize('price', ['-0.01', '1.999'])
def test_item_rejects_invalid_purchase_price(item_fields, price):
    with pytest.raises(ValidationError) as error:
        CollectionItem(purchase_price=Decimal(price), **item_fields).full_clean()
    assert 'purchase_price' in error.value.message_dict


@pytest.mark.parametrize('price', ['0', '12.50'])
def test_item_accepts_valid_purchase_price(item_fields, price):
    CollectionItem(purchase_price=Decimal(price), **item_fields).full_clean()


def test_deleting_collection_deletes_items(item_fields):
    CollectionItem.objects.create(**item_fields)
    item_fields['collection'].delete()
    assert CollectionItem.objects.count() == 0


@pytest.mark.parametrize('field', ['game', 'platform'])
def test_game_and_platform_with_items_cannot_be_deleted(item_fields, field):
    CollectionItem.objects.create(**item_fields)
    with pytest.raises(ProtectedError):
        item_fields[field].delete()
