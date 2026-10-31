import pytest
from django.apps import apps
from django.db import connection


@pytest.mark.django_db
def test_runs_on_postgresql():
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        assert cursor.fetchone() == (1,)
    assert connection.vendor == 'postgresql'


@pytest.mark.parametrize('app', ['rest_framework', 'users', 'collection', 'games', 'pricing'])
def test_app_is_installed(app):
    assert apps.is_installed(app)
