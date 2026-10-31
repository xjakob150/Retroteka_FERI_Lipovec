import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures' / 'platforms.json'

# igdb_id: (manufacturer, abbreviation). IGDB has no manufacturer and its abbreviations are uneven.
SUPPORTED = {
    59: ('Atari', '2600'),
    66: ('Atari', '5200'),
    68: ('Coleco', 'CV'),
    67: ('Mattel', 'INTV'),
    70: ('GCE', 'Vectrex'),
    18: ('Nintendo', 'NES'),
    99: ('Nintendo', 'FC'),
    64: ('Sega', 'SMS'),
    60: ('Atari', '7800'),
    19: ('Nintendo', 'SNES'),
    58: ('Nintendo', 'SFC'),
    29: ('Sega', 'MD'),
    78: ('Sega', 'Sega CD'),
    30: ('Sega', '32X'),
    86: ('NEC', 'TG-16'),
    80: ('SNK', 'Neo Geo'),
    33: ('Nintendo', 'GB'),
    35: ('Sega', 'GG'),
    61: ('Atari', 'Lynx'),
    7: ('Sony', 'PS1'),
    4: ('Nintendo', 'N64'),
    32: ('Sega', 'Saturn'),
    22: ('Nintendo', 'GBC'),
    62: ('Atari', 'Jaguar'),
    8: ('Sony', 'PS2'),
    21: ('Nintendo', 'GC'),
    11: ('Microsoft', 'Xbox'),
    23: ('Sega', 'DC'),
    24: ('Nintendo', 'GBA'),
    9: ('Sony', 'PS3'),
    12: ('Microsoft', 'X360'),
    5: ('Nintendo', 'Wii'),
    20: ('Nintendo', 'DS'),
    38: ('Sony', 'PSP'),
}


def fetch_all_platforms():
    client_id = os.environ['IGDB_CLIENT_ID']
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': os.environ['IGDB_CLIENT_SECRET'],
        'grant_type': 'client_credentials',
    }).encode()
    with urllib.request.urlopen('https://id.twitch.tv/oauth2/token', data, timeout=15) as response:
        token = json.load(response)['access_token']

    platforms = []
    while True:
        query = f'fields id,name,abbreviation,generation; limit 500; offset {len(platforms)}; sort id asc;'
        request = urllib.request.Request(
            'https://api.igdb.com/v4/platforms',
            data=query.encode(),
            headers={'Client-ID': client_id, 'Authorization': f'Bearer {token}'},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            page = json.load(response)
        platforms += page
        if len(page) < 500:
            return platforms


def to_fixture_row(platform):
    manufacturer, abbreviation = SUPPORTED.get(platform['id'], ('', platform.get('abbreviation', '')))
    return {
        'model': 'games.platform',
        # pk equals igdb_id so regenerating the fixture never moves existing rows.
        'pk': platform['id'],
        'fields': {
            'igdb_id': platform['id'],
            'name': platform['name'],
            'abbreviation': abbreviation,
            'manufacturer': manufacturer,
            'generation': platform.get('generation'),
            'is_supported': platform['id'] in SUPPORTED,
        },
    }


class Command(BaseCommand):
    help = 'Read platforms from IGDB and write the platforms fixture.'

    def handle(self, *args, **options):
        platforms = fetch_all_platforms()
        missing = SUPPORTED.keys() - {platform['id'] for platform in platforms}
        if missing:
            raise CommandError(f'Supported platforms missing from IGDB: {sorted(missing)}')

        FIXTURE.parent.mkdir(exist_ok=True)
        rows = [to_fixture_row(platform) for platform in platforms]
        FIXTURE.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        self.stdout.write(f'Wrote {len(rows)} platforms, {len(SUPPORTED)} supported, to {FIXTURE}')
