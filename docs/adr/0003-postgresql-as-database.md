# Use PostgreSQL as the database

## Context and Problem Statement

Retroteka's data is clearly relational: users own collections, collections contain items, items reference games and platforms, games are released on platforms and items have price checks ([03 – Podatkovni model](../03-podatkovni-model.md)). The model relies on foreign keys and unique constraints, e.g. `(user_id, name)` on collections and `(user_id, game_id, platform_id)` on wishlist items. Later features compare two collections (games in both, games in only one, US-17) and recommend games based on collections.

Which database should store this data?

## Decision Drivers

* Relational data with foreign keys and unique constraints.
* Genres are stored as a list of strings that is never filtered on.
* Collection comparison is a set operation on `(game, platform)` pairs.
* A path to recommendations later without adding another database.
* Free, runs in Docker ([ADR-0004](0004-docker-compose-for-local-development.md)), well supported by Django.

## Considered Options

* PostgreSQL
* MySQL
* SQLite
* MongoDB

## Decision Outcome

Chosen option: "PostgreSQL", because it is relational, fully supported by Django including the PostgreSQL-only fields in `django.contrib.postgres` (`ArrayField` for genres), supports the set operations `INTERSECT` and `EXCEPT` for comparing collections, and offers the `pgvector` extension for recommendations later. Only the backend accesses the database, through the Django ORM; migrations manage the schema.

### Consequences

* Good, because the constraints from the data model are enforced by the database, not only in code.
* Good, because comparison and statistics can be computed in SQL instead of in Python.
* Good, because recommendations can be added later with `pgvector` in the same database.
* Bad, because the code uses PostgreSQL-specific features (`ArrayField`), so switching to another database later would require changes.
* Bad, because a database server has to run during development and tests; SQLite cannot be used as a shortcut for tests.

### Confirmation

The test suite (pytest) runs against PostgreSQL in Docker Compose, the same database as in development.

## Pros and Cons of the Options

### PostgreSQL

* Good, because it is relational, with array types and extensions such as `pgvector`.
* Good, because `django.contrib.postgres` adds extra fields and lookups.
* Neutral, because it needs a running server, which Docker Compose provides.

### MySQL

* Good, because it is relational, widely used and supported by Django.
* Bad, because `django.contrib.postgres` features such as `ArrayField` are not available; genres would need a JSON field or an extra table.
* Bad, because `pgvector` is a PostgreSQL extension, so recommendations would need another solution.

### SQLite

* Good, because there is no server: one file, zero setup.
* Bad, because it is not suited to many concurrent writes from a web application.
* Bad, because there is no `ArrayField` and no `pgvector`, and development would differ from a production database.

### MongoDB

* Good, because flexible documents could store IGDB data as it arrives.
* Bad, because the data is relational and relies on joins and unique constraints across entities.
* Bad, because Django's ORM, migrations, authentication and admin are built around relational databases.

## More Information

* [03 – Podatkovni model](../03-podatkovni-model.md), [04 – Arhitektura in tehnološki sklad](../04-arhitektura-in-tehnoloski-sklad.md)
* Related: [ADR-0004](0004-docker-compose-for-local-development.md), [ADR-0013](0013-price-history-with-latest-price-on-item.md).
