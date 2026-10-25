# 05 – User Stories
## Overview

| ID | Story | Feature | Role |
|---|---|---|---|
| US-01 | Registration | #1 Registration and login with roles | Guest |
| US-02 | Login and logout | #1 Registration and login with roles | Collector |
| US-03 | Search games by title | #2 Game search via IGDB | Guest |
| US-04 | Filter search results by platform | #2 Game search via IGDB | Collector |
| US-05 | Create a collection | #3 Collections | Collector |
| US-06 | View my collections | #3 Collections | Collector |
| US-07 | Edit and delete a collection | #3 Collections | Collector |
| US-08 | Add a game to a collection | #4 Adding a game to a collection | Collector |
| US-09 | Manage an item | #4 Adding a game to a collection | Collector |
| US-10 | See whether I already own a game | #2 Game search, #4 Adding a game | Collector |
| US-11 | Browse public collections | #5 Viewing public collections | Guest |
| US-12 | Hide an inappropriate collection | #5 Viewing public collections | Moderator |
| US-13 | Estimated price of an item | #6 Estimated price and collection value | Collector |
| US-14 | Refresh an item's price | #6 Estimated price and collection value | Collector |
| US-15 | Price history of an item | #6 Estimated price and collection value | Collector |
| US-16 | Collection value | #6 Estimated price and collection value | Collector |
| US-17 | Compare collections | #7 Collection comparison | Collector |
| US-18 | Wishlist | #8 Wishlist | Collector |
| US-19 | Filter a collection | #9 Collection filters and statistics | Collector |
| US-20 | Collection statistics | #9 Collection filters and statistics | Collector |
| US-21 | Import a collection from CSV | #10 Collection import and export (CSV) | Collector |
| US-22 | Export a collection to CSV | #10 Collection import and export (CSV) | Collector |
| US-23 | Change a user's role | #11 In-app user management | Administrator |
| US-24 | Block a user account | #11 In-app user management | Administrator |

---

## Registration and login

### US-01 – Registration

- **Feature:** #1 Registration and login with roles
- **Role:** Guest
- **Story:** As a guest, I want to create an account with a username, email and password, so that I can keep my own collections.

**Acceptance criteria:**

1. The form requires a username, email, password and password confirmation. If a field is missing or the passwords do not match, no account is created and the invalid field is marked with a message.
2. If the username or email is already used, the system shows "Username is already taken" or "Email is already registered".
3. The password must be at least 8 characters long and must not consist of digits only; otherwise the system shows the reason.
4. A new account has the Collector role. The password is never shown or stored in readable form.
5. After registering, the user is logged in and taken to "My collections".

### US-02 – Login and logout

- **Feature:** #1 Registration and login with roles
- **Role:** Collector
- **Story:** As a collector, I want to log in and out, so that I can reach my collections on my computer at home and on my phone at a game fair.

**Acceptance criteria:**

1. With a correct username and password, the collector is logged in and taken to "My collections".
2. With wrong details, the system shows one message, "Invalid username or password", without saying which value was wrong.
3. **Scenario – staying logged in**
   - **Given** the collector logged in on this device 3 days ago and has not logged out,
   - **When** they open the application,
   - **Then** their collections are shown without logging in again.
4. Seven days after logging in, the collector is asked to log in again.
5. After "Log out", opening a private page such as "My collections" takes the user to the login page.

---

## Game search

### US-03 – Search games by title

- **Feature:** #2 Game search via IGDB
- **Role:** Guest (all logged-in roles can search the same way)
- **Story:** As a guest, I want to search for a retro game by title, so that I can see which platforms it was released on and what its cover looks like.

**Acceptance criteria:**

1. Search starts once at least 3 characters are entered; with fewer, the hint "Type at least 3 characters" is shown.
2. Each result shows the cover, title, release year, genre and platforms. Only platforms up to and including the 7th generation are shown; games released only on newer platforms are left out.
3. A page shows at most 20 results, with "Prev" and "Next" buttons and a counter such as "1–20 of 34".
4. If nothing is found, the system shows "No games found" and suggests checking the spelling.
5. **Scenario – game database unavailable**
   - **Given** the external game database does not respond,
   - **When** the user searches for a game that has been found before,
   - **Then** the saved result is shown with the notice "Showing saved data".

### US-04 – Filter search results by platform

- **Feature:** #2 Game search via IGDB
- **Role:** Collector
- **Story:** As a collector, I want to narrow the search to one platform, so that I quickly find the right release of a game that came out on several platforms.

**Acceptance criteria:**

1. The platform list contains only supported platforms (e.g. NES, SNES, Nintendo 64, PS1, PS2, PS3, Xbox 360, Wii).
2. With a platform selected, only games released on that platform are shown.
3. The selected platform stays selected when moving to the next page of results.
4. Reloading the page or opening a copied link shows the same search text and platform.
5. Choosing "Platform: All" removes the filter.

---

## Collections

### US-05 – Create a collection

- **Feature:** #3 Collections
- **Role:** Collector
- **Story:** As a collector, I want to create named collections, such as "PS2" or "For sale", so that I can organise my games my own way.

**Acceptance criteria:**

1. The name is required (1–100 characters); the description is optional (up to 500 characters).
2. A collector cannot have two collections with the same name; the system shows "You already have a collection with this name".
3. A new collection is private, unless the collector selects "Public" when creating it.
4. The new collection appears on "My collections" right after saving.
5. Guests do not see the "New collection" button, and a create request from a user who is not logged in is rejected.

### US-06 – View my collections

- **Feature:** #3 Collections
- **Role:** Collector
- **Story:** As a collector, I want to see all my collections and what is in them, so that I know what I own.

**Acceptance criteria:**

1. "My collections" shows only the logged-in collector's collections, each with its name, a "Public" or "Private" label, the number of items and up to five covers.
2. Opening a collection lists its items with cover, title, platform, region, condition and purchase price, sorted by title.
3. An empty collection shows "This collection is empty" and an "Add game" button.
4. A collection opens even when the external game database is unavailable.

### US-07 – Edit and delete a collection

- **Feature:** #3 Collections
- **Role:** Collector
- **Story:** As a collector, I want to rename a collection, change its visibility or delete it, so that my collections stay tidy.

**Acceptance criteria:**

1. The owner can change the name, description and visibility; the same rules apply as when creating a collection (US-05).
2. Once a collection is set to private, other users can no longer find or open it.
3. **Scenario – deleting a collection**
   - **Given** the collector has a collection with 12 items,
   - **When** they click "Delete",
   - **Then** a dialog shows the collection name and "12 items will be deleted"; after confirming, the collection and its items are gone.
4. A collection that belongs to another user cannot be edited or deleted; any attempt is rejected and nothing changes.

---

## Adding a game to a collection

### US-08 – Add a game to a collection

- **Feature:** #4 Adding a game to a collection
- **Role:** Collector
- **Story:** As a collector, I want to add a game to a collection with its platform, region, condition, purchase price and notes, so that I have a record of this exact copy.

**Acceptance criteria:**

1. "Add to collection" in the search results opens a form with the game's cover and title and the fields: collection, platform, region (PAL, NTSC-U, NTSC-J), condition (Loose, Complete in box, New / sealed), purchase price and notes.
2. The collection list contains only the collector's own collections, and the platform list only the platforms the game was released on.
3. Collection, platform, region and condition are required; a missing field is marked, e.g. "Region is required".
4. The purchase price is optional; if entered, it must be a number ≥ 0 with at most two decimal places (EUR).
5. The same game can be added more than once, even to the same collection; each entry is a separate copy.

### US-09 – Manage an item

- **Feature:** #4 Adding a game to a collection
- **Role:** Collector
- **Story:** As a collector, I want to correct an item, move it to another collection or remove it when I sell the game, so that my collection matches what I really own.

**Acceptance criteria:**

1. The item page shows the game's cover, genres, release year and description, together with the collector's data about this copy.
2. The owner can change the platform, region, condition, purchase price and notes; the same rules apply as when adding an item (US-08).
3. "Move to…" moves the item to another of the owner's collections.
4. "Remove" asks for confirmation; after confirming, the item is no longer in the collection.
5. Items in another user's collection cannot be edited, moved or removed.

### US-10 – See whether I already own a game

- **Feature:** #2 Game search via IGDB, #4 Adding a game to a collection
- **Role:** Collector
- **Story:** As a collector, I want to see in the search results which games I already own, so that I don't buy a duplicate at a game fair.

**Acceptance criteria:**

1. **Scenario – game already owned**
   - **Given** the collector owns Gran Turismo 4 for PS2 in the collection "For sale",
   - **When** they search for "gran turismo",
   - **Then** that result shows the badge "In collection · PS2 · For sale".
2. If the collector owns the game on several platforms or in several collections, the badge lists all of them.
3. The badge is based only on the logged-in collector's own collections; guests do not see it.
4. The badge is visible in the list of results without opening the game, also on a phone screen 360 px wide.

---

## Public collections

### US-11 – Browse public collections

- **Feature:** #5 Viewing public collections
- **Role:** Guest (the same applies to all logged-in roles)
- **Story:** As a guest, I want to browse other collectors' public collections, so that I can see what others collect.

**Acceptance criteria:**

1. The list of public collections is available without logging in and shows each collection's name, the owner's username and the number of items.
2. Private collections are not listed and cannot be opened through a direct link; the system shows "Collection not found".
3. A public collection shows its items with cover, title, platform, region and condition, but never the owner's purchase prices or notes.
4. Visitors who are not the owner see no buttons for editing, adding or deleting, and their attempts to change the collection are rejected.

### US-12 – Hide an inappropriate collection

- **Feature:** #5 Viewing public collections
- **Role:** Moderator
- **Story:** As a moderator, I want to hide a public collection with inappropriate content, such as an offensive name, so that the public part of the application stays suitable for everyone.

**Acceptance criteria:**

1. Moderators and administrators see a "Hide collection" button on every public collection; collectors and guests do not.
2. **Scenario – hiding a collection**
   - **Given** a public collection has an offensive name,
   - **When** the moderator clicks "Hide collection",
   - **Then** the collection disappears from the list of public collections, and others get "Collection not found" through a direct link.
3. Hiding deletes nothing: the owner still sees the collection under "My collections" with the label "Hidden by moderator" and cannot make it public again.
4. The moderator can make a hidden collection visible again.
5. The moderator cannot edit or delete another user's collection or its items.

---

## Estimated price and collection value

### US-13 – Estimated price of an item

- **Feature:** #6 Estimated price and collection value
- **Role:** Collector
- **Story:** As a collector, I want each item to get an estimated market price automatically, so that I don't have to look prices up myself.

**Acceptance criteria:**

1. When an item is saved, the system looks up current eBay listings for the same game, platform, region and condition and uses the median of their prices in EUR as the estimated price.
2. The price is shown on the item page and in the collection list with the label "estimated", the date of the check and the number of listings used (e.g. "median of 23 eBay listings").
3. If the purchase price is known, the item page also shows the difference, e.g. "Bought for €12.00 → +€6.50 (+54 %)".
4. **Scenario – no price available**
   - **Given** eBay is unavailable or has no matching listings,
   - **When** the collector saves an item,
   - **Then** the item is saved and "Price not available" is shown instead of a price.

### US-14 – Refresh an item's price

- **Feature:** #6 Estimated price and collection value
- **Role:** Collector
- **Story:** As a collector, I want to refresh an item's estimated price, so that I see its current value when market prices change.

**Acceptance criteria:**

1. The item page has a "Refresh price" button, visible only to the owner of the item.
2. After a successful refresh, the new price and today's date are shown.
3. Each item can be refreshed at most once per day; until then the button is disabled and shows "Available again tomorrow".
4. If the refresh fails, the previous price and date stay, and the message "The price cannot be refreshed right now" is shown.

### US-15 – Price history of an item

- **Feature:** #6 Estimated price and collection value
- **Role:** Collector
- **Story:** As a collector, I want to see how an item's price has changed over time, so that I can decide when to sell or buy.

**Acceptance criteria:**

1. Every price check is kept with its date, price, number of listings and source.
2. The item page shows a chart of the price over time and a table of the checks, newest first.
3. With fewer than two checks, the text "At least two price checks are needed for a chart" is shown instead of the chart.
4. **Scenario – changing the release**
   - **Given** an item has three price checks,
   - **When** the owner changes its platform, region or condition,
   - **Then** a warning says the price history will be cleared; after confirming, the old checks are removed and a new price is looked up.

### US-16 – Collection value

- **Feature:** #6 Estimated price and collection value
- **Role:** Collector
- **Story:** As a collector, I want to see what my collections are worth, so that I know their value, for example before selling.

**Acceptance criteria:**

1. A collection's value is the sum of the estimated prices of its items. Items without a price are left out and counted separately (e.g. "3 items without a price").
2. The value is shown on "My collections", on the collection page and on public collections.
3. "My collections" also shows a summary of all the collector's collections: number of collections, number of items, total estimated value and total purchase price.
4. Only the owner sees purchase prices and the purchase total; other users see only the estimated value.
5. After an item is added, changed, moved or removed, or its price is refreshed, the value shown equals the new sum.

---

## Later features

### US-17 – Compare collections

- **Feature:** #7 Collection comparison
- **Role:** Collector
- **Story:** As a collector, I want to compare my collection with another collector's public collection, so that I can see which games we both have and which only one of us has.

**Acceptance criteria:**

1. Another user's public collection has a "Compare with mine" button, where the collector chooses one of their own collections; guests do not see the button.
2. The result is split into "In both", "Only mine" and "Only theirs", each with the number of games.
3. **Scenario – matching games**
   - **Given** the collector owns Gran Turismo 4 for PS2 in the PAL region, and the other collector owns it for PS2 in the NTSC-U region,
   - **When** they compare the collections,
   - **Then** the game is listed under "In both", because games match on game and platform only.
4. The comparison never shows the other collector's purchase prices or notes.
5. A private or hidden collection cannot be compared; the system shows "Collection not found".

### US-18 – Wishlist

- **Feature:** #8 Wishlist
- **Role:** Collector
- **Story:** As a collector, I want to keep a list of games I am still looking for, so that I know what to look out for at a game fair.

**Acceptance criteria:**

1. Every collector has exactly one wishlist from the moment their account is created; it cannot be deleted.
2. "+ Wishlist" in the search results adds the game. The platform is required; region, condition and notes are optional.
3. In the search results, a game on the wishlist has the badge "On wishlist", and its button changes to "✓ On wishlist".
4. The wishlist is shown as a separate card on "My collections" with the number of games wanted, and it is not counted in the total value.
5. **Scenario – game bought**
   - **Given** a game is on the wishlist,
   - **When** the collector adds the same game and platform to one of their collections,
   - **Then** the system offers to remove it from the wishlist.

### US-19 – Filter a collection

- **Feature:** #9 Collection filters and statistics
- **Role:** Collector
- **Story:** As a collector, I want to filter a collection by platform, region and condition, so that I can quickly find games even in a collection of hundreds.

**Acceptance criteria:**

1. A collection can be filtered by platform, region and condition, and the filters can be combined (e.g. PS2 + PAL + Complete in box).
2. Active filters are shown as chips that can be removed one by one, together with a counter such as "Showing 12 of 85 items".
3. "Clear filters" removes all filters at once.
4. Reloading the page keeps the selected filters.
5. If no item matches, the system shows "No items match the selected filters".

### US-20 – Collection statistics

- **Feature:** #9 Collection filters and statistics
- **Role:** Collector
- **Story:** As a collector, I want to see statistics for a collection, so that I understand what it consists of.

**Acceptance criteria:**

1. The statistics show the number of items and the estimated value per platform, sorted by the number of items, highest first.
2. They also show the share of items by condition and by region in percent (e.g. "Loose 40% · CIB 50% · New 10%").
3. The statistics always describe the whole collection and do not change when filters are applied.
4. For an empty collection, the statistics panel shows "No statistics yet".

### US-21 – Import a collection from CSV

- **Feature:** #10 Collection import and export (CSV)
- **Role:** Collector
- **Story:** As a collector, I want to import my collection from a CSV file exported from Excel, so that I don't have to enter hundreds of games by hand.

**Acceptance criteria:**

1. A template can be downloaded. The file must be a CSV (UTF-8, comma or semicolon separator, at most 2 MB) with the columns title, platform, region, condition, purchase price and notes; other files are rejected with the reason.
2. Before anything is saved, a preview marks each row as "found", "multiple matches", "not found" or "invalid", with the total for each.
3. For "multiple matches", the collector picks the right game from a list; for "not found", they can search manually or leave the row out.
4. **Scenario – invalid row**
   - **Given** a row has the platform "PS5" or the condition "excellent",
   - **When** the collector uploads the file,
   - **Then** the row shows the reason (e.g. Unsupported platform "PS5") and is skipped, while the other rows are not affected.
5. Rows are saved into the chosen collection only after "Import" is clicked, and the import ends with a summary (e.g. "118 imported, 6 skipped").

### US-22 – Export a collection to CSV

- **Feature:** #10 Collection import and export (CSV)
- **Role:** Collector
- **Story:** As a collector, I want to export a collection to a CSV file, so that I have a backup and can work with it in Excel.

**Acceptance criteria:**

1. "Export CSV" on the collection page downloads a CSV file named after the collection (e.g. `main-shelf.csv`).
2. The file has the same columns as the import template, plus the estimated price.
3. An exported file can be imported again without any invalid rows.
4. Only the owner can export a collection.

### US-23 – Change a user's role

- **Feature:** #11 In-app user management
- **Role:** Administrator
- **Story:** As an administrator, I want to change users' roles in the application, so that I can appoint moderators quickly, without technical tools.

**Acceptance criteria:**

1. The "Users" page is available only to administrators; other roles cannot open it or use its actions.
2. Users can be searched by username or email and filtered by role and status. Each row shows the username, email, role, status and registration date.
3. The administrator can set a user's role to Collector, Moderator or Administrator; the new role applies from that user's next action.
4. The administrator cannot remove the Administrator role from themselves.
5. Passwords are never shown, and the administrator cannot change other users' collections.

### US-24 – Block a user account

- **Feature:** #11 In-app user management
- **Role:** Administrator
- **Story:** As an administrator, I want to block an account that breaks the rules, so that I can stop abuse.

**Acceptance criteria:**

1. Each user on the "Users" page has a "Block" button; a blocked user has the status "Blocked" and an "Unblock" button instead.
2. **Scenario – blocking a user**
   - **Given** a user is logged in and has public collections,
   - **When** the administrator blocks their account,
   - **Then** the user's next action is rejected, they are logged out, and their public collections disappear from the list of public collections.
3. A blocked user who tries to log in sees "Your account is blocked".
4. After "Unblock", the user can log in again and their public collections are listed again.
5. The administrator cannot block their own account.

---
