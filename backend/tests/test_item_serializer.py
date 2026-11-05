from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from collection.models import Collection, CollectionItem
from collection.serializers import ItemDetailSerializer, ItemSerializer
from games.models import Game, GameRelease, Platform

pytestmark = pytest.mark.django_db


@pytest.fixture
def owner():
    return get_user_model().objects.create_user('marko', 'marko@example.com', 'dolgo-geslo-1')


@pytest.fixture
def data(owner):
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    game = Game.objects.create(igdb_id=1601, title='Gran Turismo 4', synced_at=timezone.now())
    GameRelease.objects.create(game=game, platform=ps2, release_year=2004)
    collection = Collection.objects.create(user=owner, name='PS2')
    return {
        'collection': collection.id, 'game': game.id, 'platform': ps2.id,
        'region': 'pal', 'condition': 'cib',
    }


def serializer(owner, payload):
    return ItemSerializer(data=payload, context={'request': SimpleNamespace(user=owner)})


def errors(owner, payload):
    form = serializer(owner, payload)
    assert not form.is_valid()
    return form.errors


def test_valid_item_is_saved_without_price(owner, data):
    form = serializer(owner, data)
    assert form.is_valid(), form.errors
    item = form.save()
    assert (item.region, item.condition, item.purchase_price, item.notes) == ('pal', 'cib', None, '')
    assert item.estimated_price is None


@pytest.mark.parametrize('field, message', [
    ('collection', 'Collection is required'),
    ('game', 'Game is required'),
    ('platform', 'Platform is required'),
    ('region', 'Region is required'),
    ('condition', 'Condition is required'),
])
@pytest.mark.parametrize('missing', ['absent', None, ''])
def test_required_fields_have_story_messages(owner, data, field, message, missing):
    if missing == 'absent':
        del data[field]
    else:
        data[field] = missing
    assert errors(owner, data)[field] == [message]


def test_other_users_collection_looks_like_a_missing_one(owner, data):
    other = get_user_model().objects.create_user('ana', 'ana@example.com', 'dolgo-geslo-1')
    foreign = Collection.objects.create(user=other, name='Tuja')
    assert errors(owner, {**data, 'collection': foreign.id}) == {'collection': ['Select one of your collections.']}
    assert errors(owner, {**data, 'collection': 99999}) == {'collection': ['Select one of your collections.']}


def test_game_must_be_released_on_platform(owner, data):
    n64 = Platform.objects.create(igdb_id=4, name='Nintendo 64', abbreviation='N64', is_supported=True)
    assert errors(owner, {**data, 'platform': n64.id}) == {'platform': ['Select a platform the game was released on.']}


def test_unsupported_platform_is_rejected_even_with_release(owner, data):
    ps5 = Platform.objects.create(igdb_id=167, name='PlayStation 5', is_supported=False)
    GameRelease.objects.create(game_id=data['game'], platform=ps5)
    assert errors(owner, {**data, 'platform': ps5.id}) == {'platform': ['Select a platform the game was released on.']}


def test_unknown_game_and_platform(owner, data):
    assert errors(owner, {**data, 'game': 99999})['game'] == ['Select a game from the search results.']
    assert errors(owner, {**data, 'platform': 99999})['platform'] == ['Select a platform the game was released on.']


@pytest.mark.parametrize('field', ['region', 'condition'])
def test_unknown_region_or_condition_is_rejected(owner, data, field):
    assert field in errors(owner, {**data, field: 'neznano'})


@pytest.mark.parametrize('price', ['-0.01', '1.999', 'abc'])
def test_invalid_purchase_price_is_rejected(owner, data, price):
    assert 'purchase_price' in errors(owner, {**data, 'purchase_price': price})


@pytest.mark.parametrize('price, stored', [('0', '0.00'), ('12.5', '12.50'), (None, None)])
def test_valid_purchase_price(owner, data, price, stored):
    form = serializer(owner, {**data, 'purchase_price': price})
    assert form.is_valid(), form.errors
    item = form.save()
    assert (None if item.purchase_price is None else f'{item.purchase_price:.2f}') == stored


def test_notes_up_to_1000_characters(owner, data):
    assert serializer(owner, {**data, 'notes': 'x' * 1000}).is_valid()
    assert 'notes' in errors(owner, {**data, 'notes': 'x' * 1001})


def test_same_game_can_be_added_twice_to_same_collection(owner, data):
    for _ in range(2):
        form = serializer(owner, data)
        assert form.is_valid()
        form.save()
    assert CollectionItem.objects.count() == 2


def test_estimated_price_cannot_be_set(owner, data):
    form = serializer(owner, {**data, 'estimated_price': '99.00', 'price_checked_at': '2026-01-01T00:00:00Z'})
    assert form.is_valid()
    item = form.save()
    assert (item.estimated_price, item.price_checked_at) == (None, None)


@pytest.fixture
def item(owner, data):
    form = serializer(owner, data)
    assert form.is_valid()
    return form.save()


def editing(owner, item, payload):
    return ItemSerializer(item, data=payload, partial=True, context={'request': SimpleNamespace(user=owner)})


def test_owner_edits_copy_details(owner, item):
    form = editing(owner, item, {'region': 'ntsc_j', 'condition': 'loose', 'purchase_price': '5.00', 'notes': 'Brez škatle'})
    assert form.is_valid(), form.errors
    form.save()
    item.refresh_from_db()
    assert (item.region, item.condition, f'{item.purchase_price}', item.notes) == ('ntsc_j', 'loose', '5.00', 'Brez škatle')


def test_edit_can_clear_purchase_price(owner, item):
    form = editing(owner, item, {'purchase_price': None})
    assert form.is_valid()
    form.save()
    item.refresh_from_db()
    assert item.purchase_price is None


def test_platform_change_needs_release_of_the_same_game(owner, item):
    n64 = Platform.objects.create(igdb_id=4, name='Nintendo 64', abbreviation='N64', is_supported=True)
    form = editing(owner, item, {'platform': n64.id})
    assert not form.is_valid()
    assert form.errors == {'platform': ['Select a platform the game was released on.']}
    GameRelease.objects.create(game=item.game, platform=n64)
    assert editing(owner, item, {'platform': n64.id}).is_valid()


def test_game_cannot_be_changed(owner, item):
    other_game = Game.objects.create(igdb_id=1600, title='Gran Turismo 3', synced_at=timezone.now())
    GameRelease.objects.create(game=other_game, platform=item.platform)
    form = editing(owner, item, {'game': other_game.id})
    assert form.is_valid()
    form.save()
    item.refresh_from_db()
    assert item.game.title == 'Gran Turismo 4'


def test_item_moves_to_another_own_collection(owner, item):
    for_sale = Collection.objects.create(user=owner, name='For sale')
    form = editing(owner, item, {'collection': for_sale.id})
    assert form.is_valid()
    form.save()
    item.refresh_from_db()
    assert item.collection == for_sale


def test_item_cannot_move_to_other_users_collection(owner, item):
    foreign = Collection.objects.create(
        user=get_user_model().objects.create_user('ana', 'ana@example.com', 'dolgo-geslo-1'), name='Tuja',
    )
    form = editing(owner, item, {'collection': foreign.id})
    assert not form.is_valid()
    assert form.errors == {'collection': ['Select one of your collections.']}


def test_edit_keeps_required_rules(owner, item):
    form = editing(owner, item, {'region': ''})
    assert not form.is_valid()
    assert form.errors == {'region': ['Region is required']}


def test_detail_includes_game_description_and_platforms(owner, item):
    wii = Platform.objects.create(igdb_id=5, name='Wii', abbreviation='Wii', generation=7, is_supported=True)
    ps5 = Platform.objects.create(igdb_id=167, name='PlayStation 5', is_supported=False)
    GameRelease.objects.create(game=item.game, platform=wii, release_year=2008)
    GameRelease.objects.create(game=item.game, platform=ps5)
    item.game.genres, item.game.summary, item.game.release_year = ['Racing'], 'Dirkalna igra.', 2004
    item.game.save()
    Platform.objects.filter(igdb_id=8).update(generation=6)
    game = ItemDetailSerializer(item).data['game']
    assert (game['title'], game['genres'], game['summary'], game['release_year']) == (
        'Gran Turismo 4', ['Racing'], 'Dirkalna igra.', 2004,
    )
    assert [(platform['abbreviation'], platform['release_year']) for platform in game['platforms']] == [
        ('PS2', 2004), ('Wii', 2008),
    ]
