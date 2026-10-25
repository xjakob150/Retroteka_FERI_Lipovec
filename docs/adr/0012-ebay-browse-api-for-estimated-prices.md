# Use the eBay Browse API for estimated prices

## Context and Problem Statement

Each item in a collection should automatically get an estimated market price for its game, platform, region and condition: the median price of current eBay listings, in EUR (US-13). The owner can refresh the price at most once per day (US-14), every check is kept (US-15), and the value of a collection is the sum of its estimated prices (US-16). If no price is available, the item is still saved and shows "Price not available".

Where should prices come from, and when should they be fetched?

## Decision Drivers

* Free for a student project.
* An official API, no scraping.
* Prices in EUR.
* Saving an item must never fail because of the price source.
* The source should be replaceable if the estimates turn out to be poor.
* No extra infrastructure (workers, message queues) in the MVP.

## Considered Options

* eBay Browse API (active listings)
* eBay Marketplace Insights API (sold listings)
* PriceCharting API
* Scraping sold prices from eBay or PriceCharting pages
* Purchase price only, without market estimates

## Decision Outcome

Chosen option: "eBay Browse API", because it is the only official and free source available to this project that returns current market prices for games on all supported platforms. Details:

* The `pricing` app searches the `EBAY_DE` marketplace, so listing prices are in EUR.
* The search query combines the title and platform with keywords for region and condition (e.g. "PAL", "CIB", "complete", "sealed").
* The estimated price is the median of the prices of the matching listings; the number of listings is stored with each check (US-13).
* The price is fetched synchronously when an item is saved or refreshed, with a timeout of about 5 seconds. On a timeout or an error, the item is saved without a price.
* The eBay client sits behind a small interface in the `pricing` app, and `PriceCheck.source` records which source produced each check, so another source can be added later.
* There is no background worker (Celery, Redis) in the MVP. How prices are fetched during a CSV import (feature #10, possibly hundreds of items at once) will be decided in a separate ADR when that feature is built.

### Consequences

* Good, because it is free: the default limit of 5,000 calls per day is far more than one refresh per item per day needs.
* Good, because the median dampens outliers such as bundles, reproductions or broken copies.
* Good, because saving an item never fails because of eBay.
* Bad, because the Browse API returns active listings, i.e. asking prices, not the prices games actually sold for, so estimates tend to be higher than real sales. The UI labels the price as "estimated" and shows how many listings it is based on.
* Bad, because eBay's condition values describe wear, not completeness, so a loose cartridge and a complete-in-box copy cannot be separated by a filter. Region is an optional item detail that sellers fill in inconsistently. Both rely on keywords, which makes the matches noisy.
* Bad, because only listings on eBay Germany are used, so prices reflect that market.
* Bad, because saving an item can take up to the timeout when eBay is slow.
* Bad, because the synchronous approach does not work for importing many items at once; this stays open until the CSV import is designed.

### Confirmation

Tests with a mocked eBay client: a timeout saves the item without a price; a successful check stores a `PriceCheck` with the price, the number of listings and the source `ebay`; a second refresh on the same day is rejected.

## Pros and Cons of the Options

### eBay Browse API

* Good, because it is free, official and returns EUR prices on `EBAY_DE`.
* Bad, because it returns asking prices, cannot tell loose from complete copies and relies on noisy keyword matching.

### eBay Marketplace Insights API

* Good, because it returns sold listings, which would give more realistic prices.
* Bad, because access is restricted to approved eBay partners, so it is not available to this project.

### PriceCharting API

* Good, because its prices come from completed sales and are given separately for loose, complete-in-box and new copies, which matches Retroteka's conditions exactly.
* Bad, because API access requires a paid subscription.

### Scraping

* Good, because it would give sold prices without paying.
* Bad, because it breaks the sites' terms of use and stops working whenever the page layout changes.

### Purchase price only

* Good, because there is no external dependency.
* Bad, because it misses a core goal: knowing what a collection is worth today.

## More Information

* Feature #6 and step 5 of the key workflow in [02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md); US-13 to US-16 in [05 – User Stories](../05-uporabniske-zgodbe.md)
* If the eBay estimates are not good enough, the fallback is PriceCharting (paid). The switch would be recorded in a new ADR that supersedes this one; thanks to `PriceCheck.source`, existing history stays valid.
* Related: [ADR-0008](0008-only-backend-calls-external-apis.md), [ADR-0013](0013-price-history-with-latest-price-on-item.md).
