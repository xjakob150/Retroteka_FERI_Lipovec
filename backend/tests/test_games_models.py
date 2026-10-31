import pytest
from django.core.management import call_command
from django.db import IntegrityError
from django.utils import timezone

from games.models import Game, GameRelease, Platform

pytestmark = pytest.mark.django_db


@pytest.fixture
def platforms():
    call_command('loaddata', 'platforms', verbosity=0)


def make_game(igdb_id=1):
    return Game.objects.create(igdb_id=igdb_id, title='Gran Turismo 4', synced_at=timezone.now())


def test_fixture_loads_all_platforms_and_marks_supported(platforms):
    assert Platform.objects.count() == 220
    assert Platform.objects.filter(is_supported=True).count() == 34


def test_platforms_from_us_04_are_supported(platforms):
    supported = set(Platform.objects.filter(is_supported=True).values_list('abbreviation', flat=True))
    assert {'NES', 'SNES', 'N64', 'PS1', 'PS2', 'PS3', 'X360', 'Wii'} <= supported


def test_supported_platforms_are_at_most_generation_7_and_have_display_data(platforms):
    for platform in Platform.objects.filter(is_supported=True):
        assert platform.generation <= 7
        assert platform.abbreviation and platform.manufacturer


def test_ps5_exists_but_is_not_supported(platforms):
    assert Platform.objects.get(name='PlayStation 5').is_supported is False


def test_game_igdb_id_is_unique():
    make_game()
    with pytest.raises(IntegrityError):
        make_game()


def test_platform_igdb_id_is_unique():
    Platform.objects.create(igdb_id=1, name='A')
    with pytest.raises(IntegrityError):
        Platform.objects.create(igdb_id=1, name='B')


def test_release_is_unique_per_game_and_platform(platforms):
    game = make_game()
    ps2 = Platform.objects.get(igdb_id=8)
    GameRelease.objects.create(game=game, platform=ps2, release_year=2004)
    with pytest.raises(IntegrityError):
        GameRelease.objects.create(game=game, platform=ps2, release_year=2005)
