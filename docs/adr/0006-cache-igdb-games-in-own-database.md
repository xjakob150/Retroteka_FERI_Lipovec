# Cache games from IGDB in our own database on first use

## Context and Problem Statement

Game data comes from IGDB ([ADR-0005](0005-igdb-as-game-data-source.md)), but the application still needs part of it locally. Collection items reference a game, the item page shows the cover, genres, release year and summary (US-09), and collections must open even when IGDB is unavailable (US-06). Searching for a game that has been found before must also work when IGDB is down, with the notice "Showing saved data" (US-03). On top of that, IGDB allows only 4 requests per second for the whole application.

How much IGDB data should be stored locally, and when?

## Decision Drivers

* Collections and item pages must work without IGDB.
* Search for previously found games must work without IGDB.
* As few IGDB requests as possible, because of the shared rate limit.
* No catalogue to maintain ([ADR-0005](0005-igdb-as-game-data-source.md)) and no large import job.

## Considered Options

* Cache games on first use (when searched or added to a collection)
* Store only the IGDB ID on items and always read the rest from IGDB
* Import all retro games from IGDB and sync them periodically

## Decision Outcome

Chosen option: "Cache games on first use", because it meets the requirements for working without IGDB with the least stored data and without background jobs. It works as follows:

* Search always asks IGDB first. Every result is written to `Game` and `GameRelease` (inserted or updated) and `synced_at` is set. Games that are searched again are refreshed this way, so no separate refresh job is needed.
* If IGDB does not respond, the backend searches the stored games instead and marks the response, so the frontend shows "Showing saved data".
* Collection, item and statistics pages read only from the database and never call IGDB.
* Only what the application shows is stored: title, cover URL, release year, genres, summary and the platforms the game was released on.

### Consequences

* Good, because collections, items, collection value and statistics never depend on IGDB.
* Good, because search keeps working for any game that someone has searched for before.
* Good, because the database holds only games that people actually looked for.
* Bad, because search writes to the database on every request (up to 20 games per page).
* Bad, because the fallback search cannot find games that nobody has searched for yet.
* Bad, because data for games that nobody searches again can become outdated; `synced_at` shows how old it is.
* Neutral, because only the cover URL is stored; the images themselves still load from IGDB's image server.

### Confirmation

Tests with a mocked IGDB client: when the client raises an error, search returns stored games with the "saved data" flag; collection and item endpoints succeed while the client is set to fail on any call.

## Pros and Cons of the Options

### Cache games on first use

* Good, because it covers the offline requirements with minimal data and no jobs.
* Bad, because search also writes, and the fallback only finds games seen before.

### Store only the IGDB ID on items

* Good, because there is nothing to keep in sync.
* Bad, because every collection and item page would call IGDB, so collections would not open when IGDB is down (US-06), and the rate limit would be reached quickly.
* Bad, because sorting a collection by title (US-06) would need data from IGDB for every item.

### Import all retro games and sync them periodically

* Good, because search works fully without IGDB.
* Bad, because it is effectively an own catalogue: a large initial import, a sync job and storage for games nobody uses.
* Bad, because the import and the sync use up the shared IGDB rate limit.

## More Information

* Notes on `Game` and `synced_at` in [03 – Podatkovni model](../03-podatkovni-model.md); US-03, US-06 and US-09 in [05 – User Stories](../05-uporabniske-zgodbe.md)
* Related: [ADR-0005](0005-igdb-as-game-data-source.md), [ADR-0007](0007-platforms-as-reference-table.md), [ADR-0008](0008-only-backend-calls-external-apis.md).
