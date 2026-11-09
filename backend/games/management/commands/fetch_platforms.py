import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from games.igdb import IGDBError, get_client

FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures' / 'platforms.json'

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
    platforms = []
    while True:
        query = f'fields id,name,abbreviation,generation; limit 500; offset {len(platforms)}; sort id asc;'
        page = get_client().post('platforms', query).json()
        platforms += page
        if len(page) < 500:
            return platforms


def to_fixture_row(platform):
    manufacturer, abbreviation = SUPPORTED.get(platform['id'], ('', platform.get('abbreviation', '')))
    return {
        'model': 'games.platform',
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
        try:
            platforms = fetch_all_platforms()
        except IGDBError as error:
            raise CommandError(str(error)) from error
        missing = SUPPORTED.keys() - {platform['id'] for platform in platforms}
        if missing:
            raise CommandError(f'Supported platforms missing from IGDB: {sorted(missing)}')

        FIXTURE.parent.mkdir(exist_ok=True)
        rows = [to_fixture_row(platform) for platform in platforms]
        FIXTURE.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        self.stdout.write(f'Wrote {len(rows)} platforms, {len(SUPPORTED)} supported, to {FIXTURE}')
