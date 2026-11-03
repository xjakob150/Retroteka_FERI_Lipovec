import json

import pytest
import responses
from django.core.management import CommandError, call_command

from games.igdb import API_URL, TOKEN_URL, IGDBClient, RateLimiter
from games.management.commands import fetch_platforms
from games.management.commands.fetch_platforms import SUPPORTED

PLATFORMS_URL = API_URL + 'platforms'


@pytest.fixture
def fixture_path(tmp_path, monkeypatch):
    path = tmp_path / 'platforms.json'
    monkeypatch.setattr(fetch_platforms, 'FIXTURE', path)
    client = IGDBClient(client_id='id', client_secret='skrivnost', limiter=RateLimiter(0))
    monkeypatch.setattr(fetch_platforms, 'get_client', lambda: client)
    return path


def add_token():
    responses.post(TOKEN_URL, json={'access_token': 'zeton', 'expires_in': 5_000_000})


@responses.activate
def test_writes_fixture_from_igdb_pages(fixture_path):
    add_token()
    supported = [{'id': platform_id, 'name': f'P{platform_id}', 'generation': 6} for platform_id in SUPPORTED]
    first_page = supported + [{'id': 100_000 + n, 'name': f'Drugo {n}'} for n in range(500 - len(supported))]
    responses.post(PLATFORMS_URL, json=first_page)
    responses.post(PLATFORMS_URL, json=[{'id': 999_999, 'name': 'PlayStation 5', 'generation': 9}])
    call_command('fetch_platforms', verbosity=0)
    rows = json.loads(fixture_path.read_text())
    assert len(rows) == 501
    assert sum(row['fields']['is_supported'] for row in rows) == len(SUPPORTED)
    assert 'offset 500;' in responses.calls[-1].request.body.decode()


@responses.activate
def test_igdb_failure_becomes_command_error_and_writes_nothing(fixture_path):
    add_token()
    responses.post(PLATFORMS_URL, status=503)
    with pytest.raises(CommandError):
        call_command('fetch_platforms', verbosity=0)
    assert not fixture_path.exists()
