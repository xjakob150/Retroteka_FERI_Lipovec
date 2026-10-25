# Add the forum later as an extension of the existing backend

## Context and Problem Statement

A forum with channels, posts and comments, moderated by moderators, is planned as a later upgrade ([02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md)). The MVP focuses on the core problem: knowing what a collector owns and what it is worth. The question is whether to build the forum now, use an external community service, or add it later, and how it should fit into the application.

## Decision Drivers

* Keep the MVP focused on collections and prices.
* Reuse existing accounts and roles, since moderators already exist.
* Adding the forum must not change existing tables.
* No extra service to run.

## Considered Options

* Add the forum later as an extension of the existing backend
* Build the forum as part of the MVP
* Use an external service (a Discord server or Discourse) linked from the application

## Decision Outcome

Chosen option: "Add the forum later as an extension of the existing backend", because it keeps the MVP small while letting the forum reuse accounts, roles and the database. The forum will add three entities, `Channel`, `Post` and `Comment`, with `User` as the author, plus API endpoints in the same Django project. It is not a separate service, and existing tables do not change.

### Consequences

* Good, because the MVP is smaller and is finished sooner.
* Good, because users have one account, and moderators moderate the forum with the role they already have ([ADR-0011](0011-user-role-as-single-field.md)).
* Good, because adding the forum means only new tables with foreign keys to `User`; existing data and migrations stay untouched.
* Bad, because there are no community features at launch.
* Bad, because forum features (text formatting, pagination, reporting posts) will have to be built by hand later, while ready-made services already have them.

## Pros and Cons of the Options

### Add the forum later as an extension of the existing backend

* Good, because the MVP stays small, accounts and roles are shared, and no new service is needed.
* Bad, because the forum features have to be built later.

### Build the forum as part of the MVP

* Good, because community features are there from the start.
* Bad, because it delays the core features without helping the core problem.

### Use an external service

* Good, because it gives complete forum features with no development.
* Bad, because users need a second account, and Retroteka's roles and moderators do not apply there.
* Bad, because forum posts cannot link to collections and games inside the application.

## More Information

* "Kasnejše nadgradnje" in [02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md); "Nadgradnja: forum" in [03 – Podatkovni model](../03-podatkovni-model.md); "Forum kot nadgradnja" in [04 – Arhitektura in tehnološki sklad](../04-arhitektura-in-tehnoloski-sklad.md)
* Related: [ADR-0003](0003-postgresql-as-database.md), [ADR-0011](0011-user-role-as-single-field.md).
