from django.db import models
from django.utils import timezone

from collection.models import CollectionItem


class PriceSource(models.TextChoices):
    EBAY = 'ebay', 'eBay'


class PriceCheck(models.Model):
    """En pregled okvirne cene izvoda (US-15); zapisuje ga samo pricing.services (ADR-0013)."""

    item = models.ForeignKey(CollectionItem, on_delete=models.CASCADE, related_name='price_checks')
    checked_at = models.DateTimeField(default=timezone.now)
    # Prazna, kadar eBay ni našel nobenega oglasa ("Price not available").
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='EUR')
    listing_count = models.PositiveIntegerField()
    source = models.CharField(max_length=10, choices=PriceSource.choices, default=PriceSource.EBAY)

    class Meta:
        ordering = ['-checked_at', '-id']

    def __str__(self):
        return f'{self.item} {self.price} {self.currency} ({self.checked_at:%Y-%m-%d})'
