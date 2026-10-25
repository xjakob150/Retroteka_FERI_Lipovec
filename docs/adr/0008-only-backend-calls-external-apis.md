# Call external APIs only from the backend

## Context and Problem Statement

Retroteka uses two external APIs: IGDB for game data ([ADR-0005](0005-igdb-as-game-data-source.md)) and the eBay Browse API for prices ([ADR-0012](0012-ebay-browse-api-for-estimated-prices.md)). Both need secret credentials (a Twitch client ID and secret for IGDB, an eBay client ID and secret), and both have limits that apply to the whole application: IGDB allows 4 requests per second, eBay 5,000 calls per day. Guests can search without an account (US-03).

Should the browser call these APIs directly, or should all calls go through our backend?

## Decision Drivers

* Secret credentials must never reach the browser.
* Rate limits are shared by all users and must be controlled in one place.
* The backend has to store the results anyway (game cache in [ADR-0006](0006-cache-igdb-games-in-own-database.md), price history in [ADR-0013](0013-price-history-with-latest-price-on-item.md)).
* IGDB does not support calls from the browser (no CORS).
* The frontend should not depend on the response formats of external APIs.

## Considered Options

* Only the backend calls external APIs
* The browser calls external APIs directly
* A separate proxy service (e.g. a serverless function) in front of the APIs

## Decision Outcome

Chosen option: "Only the backend calls external APIs", because it is the only option that keeps credentials secret and lets the backend store results and enforce limits without another service. The IGDB client lives in the `games` app and the eBay client in the `pricing` app. Credentials are read from environment variables (`.env`). The backend maps external responses to its own JSON, so the frontend only knows the Retroteka API. Endpoints that trigger external calls, search and price refresh, are protected with DRF throttling, so a single client cannot use up the shared limits.

### Consequences

* Good, because credentials never appear in the frontend bundle or in the browser's network traffic.
* Good, because rate limits, timeouts and retries are handled in one place.
* Good, because a change in IGDB or eBay affects only the backend client, not the frontend.
* Good, because throttling protects the IGDB and eBay limits from heavy use by guests or scripts.
* Bad, because every search goes through our backend, which adds latency and load.
* Bad, because the backend has to obtain and renew access tokens for both APIs.
* Bad, because DRF throttling counts requests in Django's cache; with the default in-memory cache each backend process counts separately, so a shared cache is needed once the backend runs as several processes.
* Neutral, because throttle rates are set in the settings and will be tuned once real usage is known.

### Confirmation

* Code review: the frontend calls only `/api/` endpoints, and no IGDB or eBay URL or key appears in `frontend/`.
* A test checks that exceeding the search throttle returns HTTP 429.

## Pros and Cons of the Options

### Only the backend calls external APIs

* Good, because secrets, limits and storage of results are in one place.
* Bad, because of the extra hop and the load on the backend.

### The browser calls external APIs directly

* Good, because there is no load on the backend, and the backend is simpler.
* Bad, because the credentials would be exposed to every visitor.
* Bad, because IGDB does not allow calls from the browser (no CORS).
* Bad, because shared limits cannot be controlled, and results could not be stored without sending them to the backend separately.

### A separate proxy service

* Good, because it hides credentials and can be scaled on its own.
* Bad, because it is one more service to build, deploy and secure, while the backend still has to store the results.

## More Information

* "Zunanja API-ja kliče backend, ne brskalnik" in [04 – Arhitektura in tehnološki sklad](../04-arhitektura-in-tehnoloski-sklad.md)
* Related: [ADR-0005](0005-igdb-as-game-data-source.md), [ADR-0006](0006-cache-igdb-games-in-own-database.md), [ADR-0012](0012-ebay-browse-api-for-estimated-prices.md).
