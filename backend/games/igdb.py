import os
import threading
import time
from datetime import datetime, timezone
from functools import cache

import requests

TOKEN_URL = 'https://id.twitch.tv/oauth2/token'
API_URL = 'https://api.igdb.com/v4/'
TIMEOUT = 5
RENEW_BEFORE = 60
MIN_INTERVAL = 0.25
COVER_URL = 'https://images.igdb.com/igdb/image/upload/t_cover_big/{}.jpg'
GAME_TYPES = (0, 4, 8, 9, 10, 11)
SEARCH_FIELDS = (
    'name,cover.image_id,first_release_date,genres.name,summary,platforms,release_dates.platform,release_dates.y'
)


class IGDBError(Exception):
    pass


class RateLimiter:
    def __init__(self, interval):
        self.interval = interval
        self._lock = threading.Lock()
        self._last = None

    def wait(self):
        with self._lock:
            if self._last is not None:
                delay = self._last + self.interval - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
            self._last = time.monotonic()


_limiter = RateLimiter(MIN_INTERVAL)


class IGDBClient:
    def __init__(self, client_id=None, client_secret=None, limiter=None):
        self.client_id = client_id if client_id is not None else os.environ.get('IGDB_CLIENT_ID', '')
        self.client_secret = (
            client_secret if client_secret is not None else os.environ.get('IGDB_CLIENT_SECRET', '')
        )
        self.limiter = limiter or _limiter
        self._token = None
        self._token_expires_at = 0

    def _access_token(self):
        if self._token and time.monotonic() < self._token_expires_at - RENEW_BEFORE:
            return self._token
        if not self.client_id or not self.client_secret:
            raise IGDBError('IGDB_CLIENT_ID and IGDB_CLIENT_SECRET are not set')
        try:
            self.limiter.wait()
            response = requests.post(
                TOKEN_URL,
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials',
                },
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            self._token = data['access_token']
            self._token_expires_at = time.monotonic() + data['expires_in']
        except (requests.RequestException, ValueError, KeyError) as error:
            raise IGDBError(f'Could not get a Twitch token: {error}') from error
        return self._token

    def post(self, endpoint, query):
        token = self._access_token()
        try:
            self.limiter.wait()
            response = requests.post(
                API_URL + endpoint,
                data=query.encode(),
                headers={'Client-ID': self.client_id, 'Authorization': f'Bearer {token}'},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise IGDBError(f'IGDB request to {endpoint} failed: {error}') from error
        return response


    def search(self, query, platform_ids, limit=20, offset=0):
        platform_ids = {int(platform_id) for platform_id in platform_ids}
        if not platform_ids:
            return [], 0
        platforms = ','.join(str(platform_id) for platform_id in sorted(platform_ids))
        game_types = ','.join(str(game_type) for game_type in GAME_TYPES)
        response = self.post(
            'games',
            f'search "{clean_search_text(query)}"; fields {SEARCH_FIELDS}; '
            f'where platforms = ({platforms}) & game_type = ({game_types}); '
            f'limit {int(limit)}; offset {int(offset)};',
        )
        try:
            games = [to_game(game, platform_ids) for game in response.json()]
            total = int(response.headers.get('X-Count', len(games)))
        except (ValueError, KeyError, TypeError) as error:
            raise IGDBError(f'Unexpected IGDB response: {error}') from error
        return games, total


def clean_search_text(query):
    return ' '.join(query.replace('\\', ' ').replace('"', ' ').split())


def to_game(game, platform_ids):
    years = {}
    for release in game.get('release_dates', []):
        platform_id, year = release.get('platform'), release.get('y')
        if platform_id in platform_ids and year and (platform_id not in years or year < years[platform_id]):
            years[platform_id] = year
    first_release = game.get('first_release_date')
    cover = game.get('cover')
    return {
        'igdb_id': game['id'],
        'title': game['name'],
        'cover_url': COVER_URL.format(cover['image_id']) if cover else '',
        'release_year': datetime.fromtimestamp(first_release, timezone.utc).year if first_release else None,
        'genres': [genre['name'] for genre in game.get('genres', [])],
        'summary': game.get('summary', ''),
        'releases': [
            {'platform_igdb_id': platform_id, 'release_year': years.get(platform_id)}
            for platform_id in sorted(set(game.get('platforms', [])) & platform_ids)
        ],
    }


@cache
def get_client():
    return IGDBClient()
