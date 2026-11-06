import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from collection.models import Collection, CollectionItem
from collection.ownership import owned_by
from games.models import Game, Platform

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup():
    user = get_user_model().objects.create_user('marko', 'marko@example.com', 'dolgo-geslo-1')
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    ps3 = Platform.objects.create(igdb_id=9, name='PlayStation 3', abbreviation='PS3', is_supported=True)
    gt4 = Game.objects.create(igdb_id=1601, title='Gran Turismo 4', synced_at=timezone.now())
    okami = Game.objects.create(igdb_id=1700, title='Okami', synced_at=timezone.now())
    return user, ps2, ps3, gt4, okami


def add(collection, game, platform):
    return CollectionItem.objects.create(collection=collection, game=game, platform=platform, region='pal', condition='cib')


def summary(owned, game):
    return [(entry['platform']['abbreviation'], entry['collection']['name']) for entry in owned.get(game.id, [])]


def test_lists_every_platform_and_collection(setup):
    user, ps2, ps3, gt4, _ = setup
    for_sale = Collection.objects.create(user=user, name='For sale')
    main = Collection.objects.create(user=user, name='Main shelf')
    add(for_sale, gt4, ps2)
    add(main, gt4, ps2)
    add(main, gt4, ps3)
    assert summary(owned_by(user, [gt4]), gt4) == [('PS2', 'For sale'), ('PS2', 'Main shelf'), ('PS3', 'Main shelf')]


def test_several_copies_in_same_place_are_one_entry(setup):
    user, ps2, _, gt4, _ = setup
    for_sale = Collection.objects.create(user=user, name='For sale')
    for _ in range(3):
        add(for_sale, gt4, ps2)
    owned = owned_by(user, [gt4])
    assert summary(owned, gt4) == [('PS2', 'For sale')]
    assert owned[gt4.id][0] == {
        'platform': {'id': ps2.id, 'name': 'PlayStation 2', 'abbreviation': 'PS2'},
        'collection': {'id': for_sale.id, 'name': 'For sale'},
    }


def test_only_the_users_own_collections_count(setup):
    user, ps2, _, gt4, _ = setup
    other = get_user_model().objects.create_user('ana', 'ana@example.com', 'dolgo-geslo-1')
    add(Collection.objects.create(user=other, name='Anina', is_public=True), gt4, ps2)
    assert summary(owned_by(user, [gt4]), gt4) == []
    assert summary(owned_by(other, [gt4]), gt4) == [('PS2', 'Anina')]


def test_hidden_own_collection_counts(setup):
    user, ps2, _, gt4, _ = setup
    add(Collection.objects.create(user=user, name='Junk box', is_hidden=True), gt4, ps2)
    assert summary(owned_by(user, [gt4]), gt4) == [('PS2', 'Junk box')]


def test_games_without_items_and_other_games_are_separate(setup):
    user, ps2, _, gt4, okami = setup
    add(Collection.objects.create(user=user, name='PS2'), okami, ps2)
    owned = owned_by(user, [gt4, okami])
    assert summary(owned, gt4) == []
    assert summary(owned, okami) == [('PS2', 'PS2')]


def test_one_query_for_all_games(setup):
    user, ps2, ps3, gt4, okami = setup
    collection = Collection.objects.create(user=user, name='Main shelf')
    add(collection, gt4, ps2)
    add(collection, okami, ps3)
    with CaptureQueriesContext(connection) as context:
        owned_by(user, [gt4, okami])
    assert len(context) == 1
