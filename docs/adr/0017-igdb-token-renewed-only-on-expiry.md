# Keep the IGDB access token in memory and renew it only when it expires

## Context and Problem Statement

IGDB requires a Twitch access token obtained with the client credentials flow ([ADR-0005](0005-igdb-as-game-data-source.md)). Twitch returns the token with `expires_in`, about 60 days. It can also become invalid earlier, for example when a new client secret is generated in the Twitch developer console. IGDB then answers with HTTP 401.

Where should the backend keep the token, and when should it obtain a new one?

## Decision Drivers

* Search must not obtain a new token on every request.
* No secret or token should be stored where it is not needed.
* The MVP runs locally as one backend process.
* Little code, since the client is new and has no production use yet.

## Considered Options

* In memory, renewed before expiry and once after a 401
* In the database, renewed before expiry and once after a 401
* In memory, renewed only before expiry

## Decision Outcome

Chosen option: "In memory, renewed only before expiry", because it is the simplest option that avoids a token request per search, and the case it does not cover, a token revoked early, is rare and has a manual fix. The client keeps the token and its expiry time in memory and obtains a new token one minute before `expires_in` runs out, and again whenever the backend starts. A 401 from IGDB is treated like any other IGDB failure: search falls back to stored games and shows "Showing saved data" ([ADR-0006](0006-cache-igdb-games-in-own-database.md)).

### Consequences

* Good, because the client needs no extra table and no retry logic.
* Good, because the token is never written to disk.
* Bad, because a token revoked before its expiry is used until it expires, up to about 60 days, and during that time search shows only saved data. The fix is to restart the backend after changing the client secret, which is not obvious without this ADR.
* Bad, because each backend process obtains its own token after starting.
* Neutral, because the token request is counted in the 4 requests per second limit like any other IGDB request.

### Confirmation

Tests with mocked HTTP responses: the token is requested once for several searches, a new token is requested when the stored one is less than a minute from expiry, and a 401 from IGDB raises the client's error without requesting a new token.

## Pros and Cons of the Options

### In memory, renewed before expiry and once after a 401

* Good, because a revoked token is replaced on the next search, without a restart.
* Bad, because it needs retry logic, and a loop has to be avoided when the new token is rejected too, for example with a wrong client secret.

### In the database, renewed before expiry and once after a 401

* Good, because the token survives restarts and is shared by all backend processes.
* Bad, because it needs a table and a migration for something one HTTP request can obtain, and the token is stored on disk.

### In memory, renewed only before expiry

* Good, because it has the least code.
* Bad, because an early revoked token is not noticed until it expires.

## More Information

* To revisit: renewing the token once after a 401 should be added when the backend runs in production, where nobody may notice that search shows only saved data, or when the client secret is changed regularly. That change would be recorded in a new ADR that supersedes this one.
* Related: [ADR-0005](0005-igdb-as-game-data-source.md), [ADR-0006](0006-cache-igdb-games-in-own-database.md), [ADR-0008](0008-only-backend-calls-external-apis.md).
