from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower

from games.models import Game, Platform


class Region(models.TextChoices):
    PAL = 'pal', 'PAL'
    NTSC_U = 'ntsc_u', 'NTSC-U'
    NTSC_J = 'ntsc_j', 'NTSC-J'


class Condition(models.TextChoices):
    LOOSE = 'loose', 'Loose'
    CIB = 'cib', 'Complete in box'
    NEW = 'new', 'New / sealed'


class Collection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    is_public = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    hidden_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hidden_collections',
    )
    hidden_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint('user', Lower('name'), name='unique_user_collection_name'),
        ]

    def __str__(self):
        return self.name


class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='items')
    game = models.ForeignKey(Game, on_delete=models.PROTECT, related_name='collection_items')
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT, related_name='collection_items')
    region = models.CharField(max_length=10, choices=Region.choices)
    condition = models.CharField(max_length=10, choices=Condition.choices)
    purchase_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    notes = models.TextField(blank=True)
    estimated_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.game} ({self.platform}, {self.region})'
