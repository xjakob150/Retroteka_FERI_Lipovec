import logging
from decimal import Decimal

from django.db import transaction

from .ebay import EbayError, get_client
from .models import PriceCheck, PriceSource

logger = logging.getLogger(__name__)


def record_price_check(item, price, listing_count, source=PriceSource.EBAY):
    """Edini način za zapis pregleda cene (ADR-0013).

    V isti transakciji ustvari PriceCheck in na izvod prepiše njegovo ceno in čas, zato je izvod vedno
    kopija najnovejšega pregleda. Brez oglasov je cena None in izvod pokaže "Price not available".
    """
    if (price is None) != (listing_count == 0):
        raise ValueError('A price needs at least one listing, and no listings means no price.')
    price = None if price is None else Decimal(price)
    with transaction.atomic():
        check = PriceCheck.objects.create(item=item, price=price, listing_count=listing_count, source=source)
        item.estimated_price = check.price
        item.price_checked_at = check.checked_at
        item.save(update_fields=['estimated_price', 'price_checked_at'])
    return check


def clear_price_checks(item):
    """Izbriše preglede izvoda in počisti kopijo cene (ADR-0013), npr. ko izvod postane druga izdaja."""
    with transaction.atomic():
        item.price_checks.all().delete()
        item.estimated_price = None
        item.price_checked_at = None
        item.save(update_fields=['estimated_price', 'price_checked_at'])


def fetch_price(item):
    """Pridobi okvirno ceno z eBaya in jo zapiše; ob napaki eBaya vrne None in izvod ostane brez nove cene (ADR-0012)."""
    try:
        price, listing_count = get_client().price_for(item)
    except EbayError as error:
        logger.warning('eBay price for item %s failed: %s', item.pk, error)
        return None
    return record_price_check(item, price, listing_count)
