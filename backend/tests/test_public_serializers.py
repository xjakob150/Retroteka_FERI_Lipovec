from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch
from django.utils import timezone

from collection.models import Collection, CollectionItem
from collection.serializers import PublicCollectionDetailSerializer, PublicCollectionSerializer
from games.models import Game, Platform

pytestmark = pytest.mark.django_db

PRIVATE_KEYS = {'purchase_price', 'notes', 'user', 'hidden_by'}


@pytest.fixture
def collection():
    owner = get_user_model().objects.create_user('marko', 'marko@example.com', 'dolgo-geslo-1')
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    game = Game.objects.create(igdb_id=1601, title='Gran Turismo 4', cover_url='https://x/gt4.jpg', synced_at=timezone.now())
    collection = Collection.objects.create(user=owner, name='Main shelf', description='Polica', is_public=True)
    CollectionItem.objects.create(
        collection=collection, game=game, platform=ps2, region='pal', condition='cib',
        purchase_price=Decimal('12.00'), notes='Kupljeno na sejmu',
    )
    items = CollectionItem.objects.select_related('game', 'platform').order_by('game__title', 'id')
    return Collection.objects.annotate(item_count=Count('items')).prefetch_related(
        Prefetch('items', queryset=items, to_attr='items_by_title'),
    ).get(pk=collection.pk)


def test_list_entry_shows_owner_and_count_but_no_private_fields(collection):
    data = PublicCollectionSerializer(collection).data
    assert {key: data[key] for key in ['name', 'description', 'owner', 'item_count', 'is_hidden']} == {
        'name': 'Main shelf', 'description': 'Polica', 'owner': 'marko', 'item_count': 1, 'is_hidden': False,
    }
    assert not PRIVATE_KEYS & set(data)


def test_detail_items_have_no_purchase_price_or_notes(collection):
    data = PublicCollectionDetailSerializer(collection).data
    [item] = data['items']
    assert not PRIVATE_KEYS & set(data)
    assert not PRIVATE_KEYS & set(item)
    assert item['game'] == {'id': item['game']['id'], 'title': 'Gran Turismo 4', 'cover_url': 'https://x/gt4.jpg'}
    assert (item['platform']['abbreviation'], item['region_label'], item['condition_label']) == (
        'PS2', 'PAL', 'Complete in box',
    )
    serialized = str(data)
    assert 'Kupljeno na sejmu' not in serialized
    assert '12.00' not in serialized
