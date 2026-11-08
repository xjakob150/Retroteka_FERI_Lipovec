from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from collection.models import Collection, CollectionItem
from games.models import Game, Platform
from pricing.ebay import EbayError
from pricing.models import PriceCheck
from pricing.services import fetch_price, price_difference, record_price_check

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


def test_fetch_price_records_median_from_ebay(item, ebay):
    fake = ebay(result=(Decimal('18.50'), 23))
    check = fetch_price(item)
    item.refresh_from_db()
    assert fake.calls == [item]
    assert (check.price, check.listing_count, check.source) == (Decimal('18.50'), 23, 'ebay')
    assert (item.estimated_price, item.price_checked_at) == (Decimal('18.50'), check.checked_at)


def test_fetch_price_without_listings_records_price_not_available(item, ebay):
    ebay(result=(None, 0))
    check = fetch_price(item)
    item.refresh_from_db()
    assert (check.price, check.listing_count, item.estimated_price) == (None, 0, None)
    assert item.price_checked_at == check.checked_at


@pytest.mark.parametrize('message', ['timeout', 'eBay search failed: 503'])
def test_fetch_price_on_ebay_error_keeps_previous_price(item, ebay, message):
    record_price_check(item, Decimal('15.40'), 21)
    ebay(error=EbayError(message))
    assert fetch_price(item) is None
    item.refresh_from_db()
    assert (item.estimated_price, item.price_checks.count()) == (Decimal('15.40'), 1)


@pytest.mark.parametrize('estimated, purchase, expected', [
    ('18.50', '12.00', (Decimal('6.50'), 54)),
    ('9.00', '12.00', (Decimal('-3.00'), -25)),
    ('12.00', '12.00', (Decimal('0.00'), 0)),
    ('18.50', '0', (Decimal('18.50'), None)),
    ('10.00', '3.00', (Decimal('7.00'), 233)),
    ('1.00', '8.00', (Decimal('-7.00'), -88)),
])
def test_price_difference(estimated, purchase, expected):
    assert price_difference(Decimal(estimated), Decimal(purchase)) == expected


@pytest.mark.parametrize('estimated, purchase', [(None, Decimal('12')), (Decimal('18.5'), None), (None, None)])
def test_no_difference_without_both_prices(estimated, purchase):
    assert price_difference(estimated, purchase) == (None, None)
