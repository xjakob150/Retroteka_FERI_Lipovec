from types import SimpleNamespace

import pytest

from pricing.ebay import build_query

PS2 = SimpleNamespace(name='PlayStation 2', abbreviation='PS2')


def test_query_for_pal_complete_in_box():
    assert build_query('Gran Turismo 4', PS2, 'pal', 'cib') == (
        'Gran Turismo 4 (PS2, PlayStation 2) PAL (OVP, CIB, complete, Anleitung) -defekt -Konvolut -Sammlung'
    )


@pytest.mark.parametrize('region, words', [
    ('pal', ' PAL '),
    ('ntsc_u', ' (NTSC, USA, US) '),
    ('ntsc_j', ' (NTSC-J, Japan, JP) '),
])
def test_region_words(region, words):
    assert words in build_query('Okami', PS2, region, 'cib')


@pytest.mark.parametrize('condition, words', [
    ('loose', ' (lose, loose, Modul, Disc) '),
    ('cib', ' (OVP, CIB, complete, Anleitung) '),
    ('new', ' (neu, new, sealed, versiegelt) '),
])
def test_condition_words(condition, words):
    assert words in build_query('Okami', PS2, 'pal', condition)


def test_loose_excludes_listings_with_box():
    assert build_query('Okami', PS2, 'pal', 'loose').endswith('-defekt -Konvolut -Sammlung -OVP')
    assert '-OVP' not in build_query('Okami', PS2, 'pal', 'cib')


@pytest.mark.parametrize('title, cleaned', [
    ('The Legend of Zelda: Ocarina of Time', 'The Legend of Zelda Ocarina of Time'),
    ('Ratchet & Clank', 'Ratchet Clank'),
    ('Spider-Man 2', 'Spider Man 2'),
    ('"Okami" (Best of)', 'Okami Best of'),
])
def test_title_punctuation_cannot_change_the_query(title, cleaned):
    assert build_query(title, PS2, 'pal', 'cib').startswith(f'{cleaned} (PS2, PlayStation 2) ')


def test_platform_without_abbreviation_or_with_same_name():
    assert ' Wii PAL ' in build_query('Okami', SimpleNamespace(name='Wii', abbreviation='Wii'), 'pal', 'cib')
    assert ' Saturn PAL ' in build_query('Okami', SimpleNamespace(name='Saturn', abbreviation=''), 'pal', 'cib')
