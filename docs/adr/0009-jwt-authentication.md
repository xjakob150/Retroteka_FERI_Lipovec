# Authenticate API requests with JWT access and refresh tokens

## Context and Problem Statement

The frontend is a separate SPA ([ADR-0001](0001-separate-react-spa-and-rest-api.md)). Locally it runs on `localhost:5173` and the API on `localhost:8000`, so they are different origins. The user stories set concrete rules for login:

* a collector who logged in 3 days ago is still logged in on that device (US-02);
* seven days after logging in, the collector has to log in again (US-02);
* after logging out, private pages require logging in again (US-02);
* a role change applies from the user's next action (US-23);
* a blocked user's next action is rejected and they are logged out (US-24).

How should the SPA authenticate its requests to the API?

## Decision Drivers

* Works across different origins without extra CSRF handling.
* Login survives closing the browser, with a fixed limit of 7 days.
* Role changes and blocking take effect immediately, not when a token expires.
* Logging out ends the login on the server, not only in the browser.
* Fits DRF and needs little custom code.

## Considered Options

* JWT access and refresh tokens (`djangorestframework-simplejwt`)
* Django sessions with cookies
* DRF `TokenAuthentication`
* Social login (OAuth with Google or similar)

## Decision Outcome

Chosen option: "JWT access and refresh tokens", because a token sent in the `Authorization` header works across origins without cookies, so no CSRF protection is needed, and simplejwt covers the 7-day rule through configuration. Details:

* The access token is valid for 15 minutes and is kept in memory in the frontend.
* The refresh token is valid for 7 days and is kept in `localStorage`, so the login survives closing the browser.
* Refresh tokens are not rotated, so the 7 days count from login and are not extended by use (US-02).
* Logging out adds the refresh token to simplejwt's blacklist (`token_blacklist`).
* The role is not stored in the token. On every request the user is loaded from the database, the role is read from it, and inactive (blocked) users are rejected.

### Consequences

* Good, because no CSRF handling is needed: browsers do not send the token automatically.
* Good, because role changes and blocking apply on the next request (US-23, US-24).
* Good, because the 7-day limit is a setting, not custom code.
* Bad, because the usual argument for JWT, "no state on the server", does not hold here: every request reads the user from the database, and logging out writes to the blacklist table.
* Bad, because any script on the page can read a refresh token in `localStorage`. An XSS vulnerability would let an attacker stay logged in as the user for up to 7 days, so the frontend must not insert raw HTML or load untrusted third-party scripts.
* Bad, because an access token stays valid for up to 15 minutes after logout, since only refresh tokens are blacklisted. Blocked users are still rejected because of the database check.
* Bad, because the frontend has to get a new access token when the old one expires (an Axios interceptor that refreshes and retries after a 401).
* Bad, because the blacklist table grows and needs periodic cleanup (`flushexpiredtokens`).
* Neutral, because CORS still has to allow the `Authorization` header, just without cookies.

### Confirmation

pytest tests check that:

* a blocked user's still-valid access token gets HTTP 401;
* after a role change, the next request is checked against the new role;
* a refresh token older than 7 days and a refresh token used after logout are rejected.

## Pros and Cons of the Options

### JWT access and refresh tokens

* Good, because the token travels in a header, there is no CSRF problem, lifetimes are configurable and simplejwt integrates with DRF.
* Bad, because the token is stored in the browser and the frontend has to handle refreshing.

### Django sessions with cookies

* Good, because they are built into Django, and the session cookie can be `httpOnly`, which is safer against XSS.
* Good, because logging out and blocking end the session on the server immediately.
* Neutral, because sessions could meet all the login requirements from the user stories.
* Bad, because with the SPA on a different origin, cookies need CORS with credentials, `SameSite` settings and a CSRF token on every request that changes data.

### DRF `TokenAuthentication`

* Good, because it is simple: one token per user, stored in the database.
* Bad, because tokens never expire by default, so the 7-day rule would need custom code.
* Bad, because there is one token per user, so logging out on one device logs the user out everywhere.

### Social login

* Good, because there are no passwords to store.
* Bad, because registration with username, email and password is required (US-01), and it adds a dependency on external identity providers.

## More Information

* "Avtentikacija in upravljanje uporabnikov" in [04 – Arhitektura in tehnološki sklad](../04-arhitektura-in-tehnoloski-sklad.md); US-01, US-02, US-23 and US-24 in [05 – User Stories](../05-uporabniske-zgodbe.md)
* If the XSS risk becomes unacceptable, the refresh token can move to an `httpOnly` cookie. That change would be recorded in a new ADR that supersedes this one.
* Related: [ADR-0001](0001-separate-react-spa-and-rest-api.md), [ADR-0010](0010-pbkdf2-sha256-password-hashing.md), [ADR-0011](0011-user-role-as-single-field.md).
