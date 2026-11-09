import os
import re
import statistics
import time
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from functools import cache

import requests

TOKEN_URL = 'https://api.ebay.com/identity/v1/oauth2/token'
SEARCH_URL = 'https://api.ebay.com/buy/browse/v1/item_summary/search'
SCOPE = 'https://api.ebay.com/oauth/api_scope'
MARKETPLACE = 'EBAY_DE'
TIMEOUT = 5
RENEW_BEFORE = 60
VIDEO_GAMES_CATEGORY = '139973'
MAX_LISTINGS = 50

REGION_WORDS = {
    'pal': ['PAL'],
    'ntsc_u': ['NTSC', 'USA', 'US'],
    'ntsc_j': ['NTSC-J', 'Japan', 'JP'],
}
CONDITION_WORDS = {
    'loose': ['lose', 'loose', 'Modul', 'Disc'],
    'cib': ['OVP', 'CIB', 'complete', 'Anleitung'],
    'new': ['neu', 'new', 'sealed', 'versiegelt'],
}
EXCLUDED_WORDS = ['defekt', 'Konvolut', 'Sammlung']
EXCLUDED_FOR_CONDITION = {'loose': ['OVP']}


def clean(text):
    return ' '.join(re.sub(r'[^\w]+', ' ', text).split())


def any_of(words):
    return words[0] if len(words) == 1 else f'({", ".join(words)})'


def build_query(title, platform, region, condition):
    excluded = EXCLUDED_WORDS + EXCLUDED_FOR_CONDITION.get(condition, [])
    parts = [
        clean(title),
        clean(platform.abbreviation or platform.name),
        any_of(REGION_WORDS[region]),
        any_of(CONDITION_WORDS[condition]),
        *[f'-{word}' for word in excluded],
    ]
    return ' '.join(parts)


class EbayError(Exception):
    pass


class EbayClient:
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id if client_id is not None else os.environ.get('EBAY_CLIENT_ID', '')
        self.client_secret = (
            client_secret if client_secret is not None else os.environ.get('EBAY_CLIENT_SECRET', '')
        )
        self._token = None
        self._token_expires_at = 0

    def _access_token(self):
        if self._token and time.monotonic() < self._token_expires_at - RENEW_BEFORE:
            return self._token
        if not self.client_id or not self.client_secret:
            raise EbayError('EBAY_CLIENT_ID and EBAY_CLIENT_SECRET are not set')
        try:
            response = requests.post(
                TOKEN_URL,
                auth=(self.client_id, self.client_secret),
                data={'grant_type': 'client_credentials', 'scope': SCOPE},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            self._token = data['access_token']
            self._token_expires_at = time.monotonic() + data['expires_in']
        except (requests.RequestException, ValueError, KeyError) as error:
            raise EbayError(f'Could not get an eBay token: {error}') from error
        return self._token

    def search(self, params):
        token = self._access_token()
        try:
            response = requests.get(
                SEARCH_URL,
                params=params,
                headers={'Authorization': f'Bearer {token}', 'X-EBAY-C-MARKETPLACE-ID': MARKETPLACE},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as error:
            raise EbayError(f'eBay search failed: {error}') from error

    def price_for(self, item):
        data = self.search({
            'q': build_query(item.game.title, item.platform, item.region, item.condition),
            'category_ids': VIDEO_GAMES_CATEGORY,
            'filter': 'buyingOptions:{FIXED_PRICE},priceCurrency:EUR',
            'limit': MAX_LISTINGS,
        })
        prices = []
        try:
            for listing in data.get('itemSummaries', []):
                price = listing['price']
                if price['currency'] == 'EUR':
                    prices.append(Decimal(price['value']))
        except (KeyError, TypeError, InvalidOperation) as error:
            raise EbayError(f'Unexpected eBay response: {error}') from error
        if not prices:
            return None, 0
        median = Decimal(statistics.median(prices)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return median, len(prices)


@cache
def get_client():
    return EbayClient()
