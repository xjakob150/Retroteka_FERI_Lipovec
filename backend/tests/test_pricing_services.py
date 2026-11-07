from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from collection.models import Collection, CollectionItem
from games.models import Game, Platform
from pricing.models import PriceCheck
from pricing.services import record_price_check

pytestmark = pytest.mark.django_db


@pytest.fixture
def item():
    user = get_user_model().objects.create_user('marko', 'marko@example.com', 'dolgo-geslo-1')
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    game = Game.objects.create(igdb_id=1, title='Okami', synced_at=timezone.now())
    collection = Collection.objects.create(user=user, name='PS2')
    return CollectionItem.objects.create(collection=collection, game=game, platform=ps2, region='pal', condition='cib')


def newest(item):
    return item.price_checks.first()


def test_item_copies_the_newest_check(item):
    check = record_price_check(item, Decimal('18.50'), 23)
    item.refresh_from_db()
    assert (check.price, check.listing_count, check.currency, check.source) == (Decimal('18.50'), 23, 'EUR', 'ebay')
    assert (item.estimated_price, item.price_checked_at) == (newest(item).price, newest(item).checked_at)


def test_later_check_replaces_the_copy(item):
    record_price_check(item, Decimal('15.40'), 21)
    record_price_check(item, '17.20', 19)
    item.refresh_from_db()
    assert item.price_checks.count() == 2
    assert (item.estimated_price, item.price_checked_at) == (Decimal('17.20'), newest(item).checked_at)


def test_check_without_listings_clears_price_but_keeps_date(item):
    record_price_check(item, Decimal('15.40'), 21)
    check = record_price_check(item, None, 0)
    item.refresh_from_db()
    assert (check.price, check.listing_count) == (None, 0)
    assert item.estimated_price is None
    assert item.price_checked_at == check.checked_at


@pytest.mark.parametrize('price, listings', [(Decimal('10'), 0), (None, 3)])
def test_price_and_listing_count_must_agree(item, price, listings):
    with pytest.raises(ValueError):
        record_price_check(item, price, listings)
    assert not PriceCheck.objects.exists()


def test_failed_item_update_leaves_no_check(item, monkeypatch):
    def broken_save(*args, **kwargs):
        raise RuntimeError('database went away')

    monkeypatch.setattr(item, 'save', broken_save)
    with pytest.raises(RuntimeError):
        record_price_check(item, Decimal('18.50'), 23)
    assert not PriceCheck.objects.exists()
    assert CollectionItem.objects.get(pk=item.pk).estimated_price is None
