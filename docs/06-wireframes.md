# 06 – Wireframes

Greyscale wireframes of Retroteka's main screens for desktop. They show layout and content only; colours, fonts and final styling will be decided during frontend development (React + Tailwind CSS).

How to read them:

- Crossed grey boxes are placeholders for game covers; grey bars are placeholder text.
- Dark elements are primary buttons, selected options and important status badges; dashed outlines mark special or secondary elements.
- Orange numbered circles are annotations. Each image is followed by a legend that explains the numbers and links them to the user stories in `05-uporabniske-zgodbe.md`.

Each wireframe opens on Imgur through its link. The same images are also included in the `wireframes/` folder.

| # | Screen | User stories | Wireframe |
|---|---|---|---|
| 1 | Log in and create account | US-01, US-02 | [Open](https://imgur.com/a/vS34PJo) |
| 2 | Game search | US-03, US-04, US-10, US-18 | [Open](https://imgur.com/a/0gk8x6Z) |
| 3 | My collections | US-05, US-06, US-12, US-16, US-18 | [Open](https://imgur.com/a/ZKBvJsL) |
| 4 | Collection detail with filters and statistics | US-06, US-07, US-16, US-19, US-20, US-22 | [Open](https://imgur.com/a/RSvGLL6) |
| 5 | Add to collection | US-08, US-13 | [Open](https://imgur.com/a/79mcO9H) |
| 6 | Item detail with price history | US-09, US-13, US-14, US-15 | [Open](https://imgur.com/a/qFl8MLZ) |
| 7 | Public collection (moderator view) | US-11, US-12, US-16, US-17 | [Open](https://imgur.com/a/afMqrDo) |
| 8 | Compare collections | US-17 | [Open](https://imgur.com/a/AnbH2gZ) |
| 9 | CSV import preview | US-21 | [Open](https://imgur.com/a/CBY0iiq) |
| 10 | User management | US-23, US-24 | [Open](https://imgur.com/a/tWI3cw9) |

---

## 1. Log in and create account

🔗 **[Open wireframe: Log in and create account](https://imgur.com/a/vS34PJo)**

The entry page for guests, with the login form on the left and registration on the right.

1. **Login form** – username and password; on success the user goes to "My collections" (US-02).
2. **Login error** – one generic message that does not reveal whether the username or the password was wrong (US-02).
3. **Registration form** – username, email, password and password confirmation, all required (US-01).
4. **Field validation** – the invalid field is marked and explained, here "Username is already taken" (US-01).
5. **Password rules** – at least 8 characters, not only digits (US-01).
6. **Create account** – the new user is logged in as a Collector and taken to "My collections" (US-01); every account has an empty wishlist from the start (US-18).

## 2. Game search

🔗 **[Open wireframe: Game search](https://imgur.com/a/0gk8x6Z)**

The search page a collector uses to find games and check whether they already own them.

1. **Search field** – search starts after 3 characters; results are limited to retro platforms (US-03).
2. **Platform filter** – lists only supported platforms; the choice is kept between result pages and after reloading (US-04).
3. **Result** – cover, title, release year, genre and platform (US-03).
4. **"In collection" badge** – shows the platform and collection where the user already owns the game, so they don't buy a duplicate (US-10).
5. **"On wishlist" badge** – the game is on the user's wishlist (US-18).
6. **Actions** – add the game to the wishlist (US-18) or to a collection; "Add to collection" opens wireframe 5 (US-08).
7. **Pagination** – at most 20 results per page (US-03).

## 3. My collections

🔗 **[Open wireframe: My collections](https://imgur.com/a/ZKBvJsL)**

The collector's home page after logging in.

1. **Summary** – number of collections and items, total estimated value and total purchase price across all collections (US-16).
2. **Visibility label** – "Public" or "Private"; new collections are private by default (US-05).
3. **Collection card** – number of items and covers (US-06), estimated value and how many items have no price (US-16).
4. **Hidden by moderator** – the owner still sees a hidden collection, but cannot make it public again (US-12).
5. **Wishlist** – always present and cannot be deleted; it is not counted in the total value (US-18).
6. **New collection and CSV import** – create a collection (US-05) or import one from a file (US-21).

## 4. Collection detail with filters and statistics

🔗 **[Open wireframe: Collection detail](https://imgur.com/a/RSvGLL6)**

The content of a single collection.

1. **Public/private toggle** – a private collection can no longer be found or opened by others (US-07).
2. **Actions** – edit and delete with confirmation (US-07), CSV import and export (US-21, US-22) and add a game (US-08).
3. **Value bar** – estimated value, purchase total, number of items and items without a price (US-16).
4. **Filters** – by platform, region and condition; they can be combined (US-19).
5. **Active filters and counter** – removable chips, "Showing 12 of 85 items" and sorting (US-19).
6. **Item list** – platform, region, condition and purchase price (US-06), and the estimated price; "Price not available" when eBay returned no listings (US-13).
7. **Statistics** – items and value per platform, and the share by condition and region for the whole collection (US-20).

## 5. Add to collection

🔗 **[Open wireframe: Add to collection form](https://imgur.com/a/79mcO9H)**

The modal that opens after choosing a game in search.

1. **Game info** – cover, title, release year and the platforms the game was released on (US-08).
2. **Collection** – only the user's own collections can be chosen (US-08).
3. **Platform** – only platforms the game was released on (US-08).
4. **Region** – PAL, NTSC-U or NTSC-J; required, with the error shown when missing (US-08).
5. **Condition** – loose, complete in box or new/sealed; required (US-08).
6. **Purchase price** – optional, ≥ 0 with at most two decimals; notes are optional (US-08).
7. **Price note** – the estimated price is fetched from eBay after saving; if eBay is unavailable, the item is saved without a price (US-13).
8. **Add to collection** – saves the item as a new copy; the same game can be added more than once (US-08).

## 6. Item detail with price history

🔗 **[Open wireframe: Item detail with price history](https://imgur.com/a/qFl8MLZ)**

The page of a single copy in a collection.

1. **Game info** – cover, genres, description and release year (US-09).
2. **This copy** – the collector's own data about the copy (US-09).
3. **Actions** – edit, move to another collection and remove with confirmation (US-09). Changing platform, region or condition clears the price history and fetches a new price (US-15).
4. **Estimated price** – the latest price check with its date, number of eBay listings and the difference from the purchase price (US-13).
5. **Refresh price** – possible once per day per item; disabled here until tomorrow (US-14).
6. **Price chart** – the price over time; shown when there are at least two price checks (US-15).
7. **Price checks** – table of past checks with date, price, number of listings and source (US-15).

## 7. Public collection (moderator view)

🔗 **[Open wireframe: Public collection, moderator view](https://imgur.com/a/afMqrDo)**

Another collector's public collection, seen by a logged-in moderator. A guest sees the same page without the moderator bar and the compare button.

1. **Collection and owner** – name, owner's username and "Public" label (US-11).
2. **Compare with mine** – opens the comparison (wireframe 8); not shown to guests (US-17).
3. **Moderator bar** – visible only to moderators and administrators; "Hide collection" hides the collection without deleting it (US-12).
4. **Summary** – number of items (US-11) and estimated value; the purchase total is private to the owner (US-16).
5. **Item card** – cover, title, platform, region, condition and estimated price; no purchase prices or notes (US-11).
6. **Price not available** – the item has no estimated price yet (US-13).

## 8. Compare collections

🔗 **[Open wireframe: Compare collections](https://imgur.com/a/AnbH2gZ)**

The result of comparing the user's collection with another collector's public collection.

1. **Your collection** – choose which of your collections to compare (US-17).
2. **Their collection** – the public collection the comparison started from; private and hidden collections cannot be compared (US-17).
3. **Matching rule** – games match on game and platform; region and condition are ignored and purchase prices are never shown (US-17).
4. **Three groups** – "In both", "Only mine" and "Only theirs", each with a count (US-17).
5. **Different region still matches** – Gran Turismo 4 is PAL for one user and NTSC-U for the other, but is listed under "In both" (US-17).

## 9. CSV import preview

🔗 **[Open wireframe: CSV import preview](https://imgur.com/a/CBY0iiq)**

The second step of importing a collection from a CSV file exported from Excel.

1. **Steps** – Upload, Preview, Done; nothing is saved until the import is confirmed (US-21).
2. **File info** – file name, number of rows and detected separator, with a link to the CSV template (US-21).
3. **Target collection** – the collection the rows are imported into (US-21).
4. **Summary** – how many rows were found, have multiple matches, were not found or are invalid (US-21).
5. **Multiple matches** – the user picks the right game from a list (US-21).
6. **Invalid row** – the reason is shown (unsupported platform, unknown condition) and the row is skipped (US-21).
7. **Not found** – the game was not found; the user can search for it manually (US-21).
8. **Import** – imports the valid rows (US-21); imported items then get their estimated prices (US-13).

## 10. User management

🔗 **[Open wireframe: User management](https://imgur.com/a/tWI3cw9)**

The administrator's page for managing users inside the application.

1. **Search and filters** – search by username or email and filter by role and status (US-23).
2. **Role** – the administrator changes a user's role; it applies from the user's next action (US-23).
3. **Own account** – the administrator cannot remove their own admin role (US-23) or block themselves (US-24).
4. **Block** – a blocked user is logged out and cannot log in (US-24).
5. **Blocked status** – a blocked account can be unblocked; while blocked, its public collections are hidden (US-24).
6. **Rules note** – passwords are never shown and administrators cannot change other users' collections (US-23, US-24).