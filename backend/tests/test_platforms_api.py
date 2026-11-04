import pytest
from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def platforms():
    call_command('loaddata', 'platforms', verbosity=0)


def get_platforms():
    return APIClient().get(reverse('platform-list'))


def test_guest_gets_only_supported_platforms(platforms):
    response = get_platforms()
    assert response.status_code == 200
    assert len(response.data) == 34
    abbreviations = {platform['abbreviation'] for platform in response.data}
    assert {'NES', 'FC', 'SNES', 'SFC', 'N64', 'PS1', 'PS2', 'PS3', 'X360', 'Wii'} <= abbreviations
    assert not any(platform['name'] == 'PlayStation 5' for platform in response.data)


def test_platforms_are_sorted_by_generation_then_name(platforms):
    data = get_platforms().data
    keys = [(platform['generation'], platform['name']) for platform in data]
    assert keys == sorted(keys)
    assert data[0]['generation'] == 2
    assert data[-1]['generation'] == 7


def test_platform_fields(platforms):
    ps2 = next(platform for platform in get_platforms().data if platform['abbreviation'] == 'PS2')
    assert set(ps2) == {'id', 'name', 'abbreviation', 'manufacturer', 'generation'}
    assert (ps2['name'], ps2['manufacturer'], ps2['generation']) == ('PlayStation 2', 'Sony', 6)


def test_platform_list_is_not_paginated(platforms):
    assert isinstance(get_platforms().data, list)
