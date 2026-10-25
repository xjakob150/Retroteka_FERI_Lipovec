# Keep price history as its own entity and copy the latest price onto the item

## Context and Problem Statement

Every price check of an item is kept with its date, price, number of listings and source, and the item page shows a chart and a table of them (US-15). Many screens, however, need only the latest price: the collection list, the value of each collection on "My collections" and on public collections, and the summary of all of a user's collections (US-16). A price can be refreshed at most once per day per item (US-14). When the owner changes the platform, region or condition, the old checks no longer describe this copy (US-15).

How should prices be stored so that both the history and the latest value are easy to use?

## Decision Drivers

* Full price history per item (US-15).
* Fast collection lists and value sums for many collections at once (US-16).
* A simple check of the once-per-day rule (US-14).
* Consistency: the latest price shown must equal the newest check.

## Considered Options

* A `PriceCheck` table, with the latest price also stored on the item
* A `PriceCheck` table only, with the latest price found by a subquery
* The latest price on the item only, without history
* History as a JSON list on the item

## Decision Outcome

Chosen option: "A `PriceCheck` table, with the latest price also stored on the item", because the history stays a proper table while lists and sums read plain columns. `CollectionItem.estimated_price` and `price_checked_at` are a deliberate copy of the newest `PriceCheck`. A single function in the `pricing` app creates a check and updates the item in the same database transaction. Changing the platform, region or condition deletes the item's checks, clears the copied price and fetches a new one.

### Consequences

* Good, because the value of a collection is a simple `SUM(estimated_price)` over its items, with no subquery per item.
* Good, because the once-per-day rule only reads `price_checked_at` on the item.
* Good, because the history can be charted and queried like any other table.
* Bad, because the same value is stored twice and can drift apart if a check is written without going through the pricing function.
* Bad, because the history table keeps growing, by at most one row per item per day.

### Confirmation

Tests: after a check, the item's `estimated_price` and `price_checked_at` equal the newest `PriceCheck`; after changing the platform, the item has no checks and no copied price until a new check succeeds.

## Pros and Cons of the Options

### `PriceCheck` table with the latest price on the item

* Good, because it gives both a full history and fast lists.
* Bad, because the duplicated value has to be kept consistent.

### `PriceCheck` table only

* Good, because no data is duplicated: there is a single source of truth.
* Bad, because every list and sum has to find the newest check per item (a subquery or window function), across all of a user's collections.
* Bad, because the once-per-day check needs a query on the history.

### Latest price on the item only

* Good, because it is the simplest.
* Bad, because there is no history, so US-15 cannot be met.

### History as a JSON list on the item

* Good, because there is one row per item.
* Bad, because there are no constraints or foreign keys, the data is hard to query and aggregate, and the whole list is rewritten on every check.

## More Information

* "Zgodovina cen je svoja entiteta" in the notes of [03 – Podatkovni model](../03-podatkovni-model.md); US-14 to US-16 in [05 – User Stories](../05-uporabniske-zgodbe.md)
* Related: [ADR-0003](0003-postgresql-as-database.md), [ADR-0012](0012-ebay-browse-api-for-estimated-prices.md).
