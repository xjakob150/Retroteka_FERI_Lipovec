from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from collection.models import Collection, CollectionItem
from games.models import Game, Platform
from pricing.models import PriceCheck

pytestmark = pytest.mark.django_db


@pytest.fixture
def item():
    user = get_user_model().objects.create_user('marko', 'marko@example.com', 'dolgo-geslo-1')
    ps2 = Platform.objects.create(igdb_id=8, name='PlayStation 2', abbreviation='PS2', is_supported=True)
    game = Game.objects.create(igdb_id=1, title='Okami', synced_at=timezone.now())
    collection = Collection.objects.create(user=user, name='PS2')
    return CollectionItem.objects.create(collection=collection, game=game, platform=ps2, region='pal', condition='cib')


def test_defaults_are_eur_ebay_and_now(item):
    check = PriceCheck.objects.create(item=item, price='18.50', listing_count=23)
    assert (check.currency, check.source) == ('EUR', 'ebay')
    assert timezone.now() - check.checked_at < timedelta(seconds=5)


def test_price_can_be_empty_when_no_listings_were_found(item):
    check = PriceCheck.objects.create(item=item, price=None, listing_count=0)
    check.refresh_from_db()
    assert check.price is None


def test_newest_check_comes_first(item):
    now = timezone.now()
    older = PriceCheck.objects.create(item=item, price='15.00', listing_count=20, checked_at=now - timedelta(days=2))
    newest = PriceCheck.objects.create(item=item, price='18.50', listing_count=23, checked_at=now)
    assert list(item.price_checks.all()) == [newest, older]


def test_deleting_item_deletes_its_checks(item):
    PriceCheck.objects.create(item=item, price='18.50', listing_count=23)
    item.delete()
    assert not PriceCheck.objects.exists()
