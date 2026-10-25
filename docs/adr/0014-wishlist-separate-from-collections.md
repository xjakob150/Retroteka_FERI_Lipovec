# Store wishlist items directly on the user, separate from collections

## Context and Problem Statement

A collector keeps a list of games they are still looking for (US-18). Every collector has exactly one wishlist from the moment the account is created, and it cannot be deleted. It is not counted in the value of collections. A wish is not a copy the collector owns: only the platform is required, region, condition and notes are optional, and there is no purchase price or price history. The same game and platform can be on the wishlist only once, while a collection may hold several copies of the same game (US-08). When the collector adds a wished-for game to a collection, the system offers to remove it from the wishlist.

Should the wishlist be a kind of collection, or something separate?

## Decision Drivers

* Exactly one wishlist per user, always present, never deleted.
* Wishes must not appear in collection value, statistics, comparison or the "In collection" badge (US-10).
* Different rules: region and condition are optional, and each game and platform can be wished for only once.
* Rules for collections should stay free of wishlist exceptions.

## Considered Options

* `WishlistItem` linked directly to the user
* The wishlist as a collection with a flag (e.g. `is_wishlist`)
* A separate `Wishlist` entity (one per user) with its own items

## Decision Outcome

Chosen option: "`WishlistItem` linked directly to the user", because the wishlist is simply all of a user's wishlist items: it exists from registration (as an empty list) and cannot be deleted, without any extra code. Collections and wishes keep their own rules and constraints, e.g. a unique `(user_id, game_id, platform_id)` for wishes.

### Consequences

* Good, because "always exists and cannot be deleted" holds by design.
* Good, because collection value, statistics, comparison, CSV import and export, and the "In collection" badge work on collections without exceptions.
* Good, because region and condition stay required for items and optional for wishes.
* Bad, because the wishlist needs its own endpoints, serializers and UI card instead of reusing those of collections.
* Bad, because turning a wish into an item touches two entities: an item is created and the wish is deleted.
* Bad, because if the wishlist ever needs properties of its own, such as a name or public sharing, a `Wishlist` table would have to be added with a migration.

### Confirmation

Tests: a new user has an empty wishlist without any setup; collection value and the "In collection" badge ignore wishes; adding the same game and platform to the wishlist twice is rejected.

## Pros and Cons of the Options

### `WishlistItem` linked directly to the user

* Good, because there is no extra entity and the rules stay clean.
* Bad, because it needs separate endpoints and UI.

### The wishlist as a collection with a flag

* Good, because it reuses the collection endpoints, UI and item model.
* Bad, because every collection rule needs an exception: the wishlist cannot be deleted, is not counted in value, and is left out of statistics, comparison and the badge.
* Bad, because region and condition on `CollectionItem` would either have to become optional for everyone or be validated differently depending on the flag.
* Bad, because collection names are unique per user, so the wishlist's name would block a user's collection with the same name.

### A separate `Wishlist` entity

* Good, because it would be a natural place for future wishlist properties.
* Bad, because it is a table with nothing but `user_id`, which has to be created at registration and kept in a one-to-one relation.

## More Information

* Feature #8 in [02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md); "Seznam želja ni zbirka" in [03 – Podatkovni model](../03-podatkovni-model.md); US-18 in [05 – User Stories](../05-uporabniske-zgodbe.md); wireframe 3 in [06 – Wireframes](../06-wireframes.md)
* Related: [ADR-0013](0013-price-history-with-latest-price-on-item.md) (wishes have no price history).
