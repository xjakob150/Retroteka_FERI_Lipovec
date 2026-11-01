from django.contrib.postgres.fields import ArrayField
from django.db import models


class Platform(models.Model):
    igdb_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=50, blank=True)
    manufacturer = models.CharField(max_length=50, blank=True)
    generation = models.PositiveSmallIntegerField(null=True, blank=True)
    is_supported = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Game(models.Model):
    igdb_id = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=255)
    cover_url = models.URLField(blank=True)
    release_year = models.PositiveSmallIntegerField(null=True, blank=True)
    genres = ArrayField(models.CharField(max_length=100), default=list, blank=True)
    summary = models.TextField(blank=True)
    synced_at = models.DateTimeField()
    platforms = models.ManyToManyField(Platform, through='GameRelease', related_name='games')

    def __str__(self):
        return self.title


class GameRelease(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='releases')
    platform = models.ForeignKey(Platform, on_delete=models.PROTECT, related_name='releases')
    release_year = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['game', 'platform'], name='unique_game_platform'),
        ]

    def __str__(self):
        return f'{self.game} ({self.platform})'
