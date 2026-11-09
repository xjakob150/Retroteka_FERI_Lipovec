import logging
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from .ebay import EbayError, get_client
from .models import PriceCheck, PriceSource

logger = logging.getLogger(__name__)


def record_price_check(item, price, listing_count, source=PriceSource.EBAY):
    if (price is None) != (listing_count == 0):
        raise ValueError('A price needs at least one listing, and no listings means no price.')
    price = None if price is None else Decimal(price)
    with transaction.atomic():
        check = PriceCheck.objects.create(item=item, price=price, listing_count=listing_count, source=source)
        item.estimated_price = check.price
        item.price_checked_at = check.checked_at
        item.save(update_fields=['estimated_price', 'price_checked_at'])
    return check


def can_refresh_price(item):
    checked_at = item.price_checked_at
    return checked_at is None or timezone.localdate(checked_at) < timezone.localdate()


def clear_price_checks(item):
    with transaction.atomic():
        item.price_checks.all().delete()
        item.estimated_price = None
        item.price_checked_at = None
        item.save(update_fields=['estimated_price', 'price_checked_at'])


def fetch_price(item):
    try:
        price, listing_count = get_client().price_for(item)
    except EbayError as error:
        logger.warning('eBay price for item %s failed: %s', item.pk, error)
        return None
    return record_price_check(item, price, listing_count)


def price_difference(estimated_price, purchase_price):
    if estimated_price is None or purchase_price is None:
        return None, None
    difference = (estimated_price - purchase_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if purchase_price == 0:
        return difference, None
    percent = (difference / purchase_price * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return difference, int(percent)
