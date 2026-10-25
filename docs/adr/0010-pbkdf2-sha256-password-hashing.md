# Hash passwords with PBKDF2-SHA256

## Context and Problem Statement

Retroteka stores a password for every account. A password must never be stored or shown in readable form (US-01, US-23), not even to administrators. If the database ever leaked, recovering the original passwords from it should be as expensive as possible.

A stored password hash is one-way: at login the entered password is hashed again and the two hashes are compared. An attacker with a leaked database can only guess passwords and hash every guess. With a fast hash function such as plain SHA-256, a GPU can try billions of guesses per second. Password hashing functions are deliberately slow and add a random salt to every password, so each guess is expensive and two identical passwords produce different hashes.

Which algorithm should hash the passwords?

## Decision Drivers

* Passwords must be salted and slow to guess.
* The algorithm must be accepted by current recommendations (OWASP Password Storage Cheat Sheet).
* No extra dependencies or configuration, if possible.
* It must be possible to switch algorithms later without forcing users to reset their passwords.

## Considered Options

* PBKDF2-SHA256 (Django's default)
* Argon2id
* bcrypt
* Plain SHA-256

## Decision Outcome

Chosen option: "PBKDF2-SHA256", because it is Django's default password hasher, needs no extra package, is accepted by OWASP when used with a high iteration count, and Django raises the iteration count with each release. The decision is cheap to reverse: Django verifies old hashes with any hasher listed in `PASSWORD_HASHERS` and re-hashes the password with the preferred hasher on the user's next login. Moving to Argon2id later only means installing `argon2-cffi` and putting the Argon2 hasher first in the list.

The password rules from US-01 (at least 8 characters, not digits only) use Django's built-in validators `MinimumLengthValidator` and `NumericPasswordValidator`.

### Consequences

* Good, because salting and iterations work out of the box, with no configuration.
* Good, because the iteration count grows with Django upgrades, and existing hashes are upgraded when users log in.
* Good, because switching to Argon2id later does not require a password reset.
* Bad, because PBKDF2 is not memory-hard: with GPUs, an attacker can test guesses faster than against Argon2id at the same login cost.
* Bad, because every login deliberately costs noticeable CPU time on the server, so repeated login attempts also put load on the server.

### Confirmation

A test checks that a stored password starts with `pbkdf2_sha256$` and does not contain the plain-text password.

## Pros and Cons of the Options

### PBKDF2-SHA256

* Good, because it is the default, needs no dependencies, is salted and iterated, and is accepted by OWASP.
* Bad, because it is not memory-hard.

### Argon2id

* Good, because it is OWASP's first recommendation and memory-hard, which makes GPU attacks much more expensive.
* Bad, because it needs the `argon2-cffi` package with a compiled library, and its memory and time parameters have to be understood and chosen.

### bcrypt

* Good, because it is proven and slow by design.
* Bad, because it needs the `bcrypt` package and only uses the first 72 bytes of a password (Django works around this by hashing the password with SHA-256 first).
* Neutral, because it has no clear advantage over PBKDF2 for this project.

### Plain SHA-256

* Good, because it is simple and fast.
* Bad, because being fast is exactly the problem: billions of guesses per second.
* Bad, because without a salt, identical passwords have identical hashes and precomputed tables (rainbow tables) can be used.

## More Information

* "JWT in PBKDF2-SHA256" in [04 – Arhitektura in tehnološki sklad](../04-arhitektura-in-tehnoloski-sklad.md)
* [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
* Related: [ADR-0009](0009-jwt-authentication.md).
