# Store platforms as a reference table seeded from an IGDB fixture

## Context and Problem Statement

Retroteka supports physical games for platforms up to and including the 7th generation (PS3, Xbox 360, Wii). Several parts of the application need the platforms before any game is in the database:

* the search filter lists only supported platforms (US-04);
* the add form offers only platforms the game was released on (US-08);
* statistics count items per platform (US-20);
* the CSV import must reject an unknown or unsupported platform with a reason (US-21).

How should platforms be represented?

## Decision Drivers

* The list of supported platforms must exist before the first game is stored.
* Items, wishes and game releases must reference a valid platform.
* The scope rule (physical games, up to the 7th generation) should be data in one place, not conditions spread through the code.
* Platforms must map to IGDB IDs, because search results and release data use them.
* Names and abbreviations are needed for display and for matching CSV values such as "PS2".

## Considered Options

* Reference table `Platform`, seeded from a fixture generated from IGDB
* Free-text platform name on the item
* Django `choices` (an enumeration in code)
* Read platforms from IGDB at runtime

## Decision Outcome

Chosen option: "Reference table `Platform`, seeded from a fixture", because foreign keys guarantee valid platforms and the list exists right after setup, before any game is stored. A management command reads the platforms from IGDB once and writes the fixture `platforms.json`, which is committed to the repository and loaded with `python manage.py loaddata platforms`. Each platform keeps its `igdb_id`, `name`, `abbreviation`, `manufacturer` and `generation`. The field `is_supported` decides what is in scope; `generation` is used only for display and sorting, because the generation alone does not define the scope (PC or digital-only platforms, for example).

### Consequences

* Good, because `CollectionItem`, `WishlistItem` and `GameRelease` have foreign keys to `Platform`, so an invalid platform cannot be stored.
* Good, because the search filter, the add form, statistics and CSV validation all use the same list.
* Good, because changing the scope is a data change (`is_supported`), not a code change.
* Bad, because the fixture has to be regenerated or edited when IGDB adds or changes platforms or when the scope changes.
* Bad, because platforms are tied to IGDB IDs; a different game data source would need a mapping.
* Bad, because CSV values do not always match names exactly ("PS2" vs "PlayStation 2"), so the import has to match both `name` and `abbreviation`.

### Confirmation

After `loaddata platforms`, the supported platforms listed in US-04 exist with `is_supported = true`. A test checks that adding an item for a platform the game was not released on is rejected.

## Pros and Cons of the Options

### Reference table seeded from a fixture

* Good, because of foreign keys, platform metadata and one shared list, with the scope stored as data.
* Bad, because the fixture has to be maintained.

### Free-text platform name

* Good, because it is the simplest.
* Bad, because nothing is validated: "PS2", "PlayStation 2" and "ps2" would count as different platforms in statistics.
* Bad, because there is no way to record which platforms a game was released on.

### Django `choices`

* Good, because values are validated without an extra table.
* Bad, because it cannot cleanly hold the IGDB ID, generation and manufacturer, and `GameRelease` needs a table to reference.
* Bad, because every change requires a code change and a migration.

### Read platforms from IGDB at runtime

* Good, because the list is always up to date.
* Bad, because the filter and forms would not work when IGDB is down, and every page load would use the shared rate limit.
* Bad, because there would be no foreign keys.

## More Information

* "Platforma je entiteta, ne niz" in the notes of [03 – Podatkovni model](../03-podatkovni-model.md)
* Related: [ADR-0005](0005-igdb-as-game-data-source.md), [ADR-0006](0006-cache-igdb-games-in-own-database.md).
