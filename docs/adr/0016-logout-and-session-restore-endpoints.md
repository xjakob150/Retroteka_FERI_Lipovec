# Log out with the refresh token alone and restore the session through a separate endpoint

## Context and Problem Statement

[ADR-0009](0009-jwt-authentication.md) decides that the access token lives in memory, the refresh token lives in `localStorage`, and logging out adds the refresh token to a blacklist. It leaves two things open.

The access token expires after 15 minutes, so a user who leaves a tab open may click "Log out" with an expired access token. What should the logout endpoint require, and how should it answer when the token is already invalid?

Reloading the page clears memory, so only the refresh token remains, and simplejwt's refresh endpoint returns only an access token. How does the frontend learn who the user is and what role they have after a reload?

This ADR adds to ADR-0009 and does not replace any part of it.

## Decision Drivers

* Logging out must end the login on the server, even when the access token has expired (US-02).
* The user must never see an error when logging out, because the outcome they want is that they are logged out.
* After a reload, the displayed username and role must reflect the database, because role changes apply from the next action (US-23).
* `localStorage` must hold no more than the refresh token, to limit what a script could read ([ADR-0009](0009-jwt-authentication.md)).

## Considered Options

For logging out:

* The refresh token alone, with a repeated logout counted as success
* Both an access token and a refresh token
* The refresh token alone, with an invalid token rejected

For restoring the session:

* A separate `GET /api/auth/me/` endpoint
* The refresh endpoint also returns the user
* The frontend keeps the user in `localStorage`

## Decision Outcome

Chosen for logging out: "The refresh token alone, with a repeated logout counted as success", because holding a refresh token is already proof of the right to revoke it, and logging out then works without first refreshing an expired access token. `POST /api/auth/logout/` is public and returns 204 for a valid, expired, already revoked or malformed token, and 400 only when no token is sent.

Chosen for restoring the session: "A separate `GET /api/auth/me/` endpoint", because it reads the current user from the database and leaves simplejwt's refresh endpoint nearly unchanged. After a reload the frontend calls refresh and then `me`.

### Consequences

* Good, because logging out does not depend on the state of the access token.
* Good, because the frontend has no logout error case to handle.
* Good, because the username and role shown after a reload are always current, and `localStorage` still holds only the refresh token.
* Good, because `me` is a protected endpoint that confirms a blocked user's valid access token gets HTTP 401.
* Bad, because a forged token also gets 204, so the answer does not prove that anything was revoked. It reveals nothing and changes nothing.
* Bad, because each page load makes one extra request.
* Neutral, because an access token stays valid for up to 15 minutes after logout, as already accepted in ADR-0009.

### Confirmation

pytest tests check that:

* logging out with an expired access token or none at all revokes the refresh token, which can then no longer be used to refresh;
* logging out again, or with an expired or malformed token, returns 204, and logging out without a token returns 400;
* `me` returns the current role after a role change, and returns 401 for a blocked user and for a request with no token.

## Pros and Cons of the Options

### The refresh token alone, with a repeated logout counted as success

* Good, because logging out always succeeds and needs no preceding refresh.
* Bad, because the answer does not say whether a token was actually revoked.

### Both an access token and a refresh token

* Good, because the server can check that both tokens belong to the same user.
* Bad, because the frontend must refresh before logging out, and if that fails the refresh token stays valid.

### The refresh token alone, with an invalid token rejected

* Good, because the answer is more precise.
* Bad, because the frontend has to ignore the error anyway, since the user counts as logged out.

### A separate `GET /api/auth/me/` endpoint

* Good, because the user data comes from one small, protected endpoint.
* Bad, because a page load needs two requests.

### The refresh endpoint also returns the user

* Good, because a page load needs one request and no new endpoint.
* Bad, because simplejwt's serializer has to be replaced, and user data is sent on every refresh, when the frontend does not need it.

### The frontend keeps the user in `localStorage`

* Good, because no extra request is needed.
* Bad, because the displayed role can be out of date.
* Bad, because it stores more in `localStorage` than ADR-0009 allows.

## More Information

* US-02, US-23 and US-24 in [05 – User Stories](../05-uporabniske-zgodbe.md)
* Related: [ADR-0009](0009-jwt-authentication.md).
