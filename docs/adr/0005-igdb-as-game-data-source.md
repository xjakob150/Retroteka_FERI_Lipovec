# Read game data from IGDB instead of keeping our own catalogue

## Context and Problem Statement

When adding a game to a collection, the collector should only describe their own copy (platform, region, condition, price), not type in the game's title, cover, release year and platforms ([01 – Zasnova rešitve](../01-zasnova-resitve.md)). That requires a source of game data that covers retro platforms up to and including the 7th generation. The backend must also check that the game was released on the platform the collector selects (key workflow, step 3, in [02](../02-funkcionalnosti-in-obseg.md)), and it needs a list of platforms with their generation to define which platforms are supported ([ADR-0007](0007-platforms-as-reference-table.md)).

Where should data about games come from?

## Decision Drivers

* No manual maintenance of thousands of games across all retro platforms. An own game database is explicitly out of scope (02).
* Good coverage of retro platforms up to the 7th generation.
* Release information per platform, to fill `GameRelease` and validate the selected platform.
* Platform records with a generation and stable IDs, to seed the platform list.
* Covers, genres and summaries for display.
* Free for a non-commercial student project.

## Considered Options

* IGDB API
* Own catalogue entered by hand
* RAWG API
* TheGamesDB API

## Decision Outcome

Chosen option: "IGDB API", because it covers retro platforms, provides release dates per platform and platform records with a generation, and is free for non-commercial use. Only the data the application shows is stored locally ([ADR-0006](0006-cache-igdb-games-in-own-database.md)), and only the backend calls IGDB ([ADR-0008](0008-only-backend-calls-external-apis.md)).

### Consequences

* Good, because there is no catalogue to build or maintain, and new games appear as IGDB adds them.
* Good, because `GameRelease` and the platform check come straight from IGDB release data.
* Good, because the platform fixture can be generated from IGDB platform records, with the same IDs as the game data ([ADR-0007](0007-platforms-as-reference-table.md)).
* Bad, because the application depends on an external service. When IGDB is down, search only finds games stored earlier ([ADR-0006](0006-cache-igdb-games-in-own-database.md)).
* Bad, because access requires a Twitch developer account and an OAuth token (client credentials) that the backend must obtain and renew.
* Bad, because IGDB allows 4 requests per second, and this limit is shared by all users of the application ([ADR-0008](0008-only-backend-calls-external-apis.md)).
* Neutral, because data quality is outside our control: wrong data can only be fixed in IGDB, not in Retroteka.

## Pros and Cons of the Options

### IGDB API

* Good, because it has broad coverage, including retro platforms.
* Good, because it provides release dates per platform and a generation for each platform.
* Good, because it is free for non-commercial use.
* Bad, because it needs Twitch OAuth, allows 4 requests per second and cannot be called from the browser (no CORS support).

### Own catalogue entered by hand

* Good, because we would have full control over the data and no external dependency.
* Bad, because thousands of games would have to be entered and corrected by hand, which is exactly the work Retroteka wants to save collectors.
* Bad, because an own game database is explicitly out of scope (02).

### RAWG API

* Good, because it offers a free API key and a large database.
* Bad, because its platform records have no generation, so supported platforms would have to be classified by hand.
* Neutral, because the free tier requires attribution (a link to RAWG) in the application.

### TheGamesDB API

* Good, because it focuses on retro platforms.
* Bad, because API keys come with a fixed monthly request allowance, which open guest search (US-03) would quickly use up.

## More Information

* [01 – Zasnova rešitve](../01-zasnova-resitve.md), [02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md), [03 – Podatkovni model](../03-podatkovni-model.md)
* The IGDB client is isolated in the `games` app. If IGDB access or terms change, a new source would be chosen in a new ADR that supersedes this one.
* Related: [ADR-0006](0006-cache-igdb-games-in-own-database.md), [ADR-0007](0007-platforms-as-reference-table.md), [ADR-0008](0008-only-backend-calls-external-apis.md).
