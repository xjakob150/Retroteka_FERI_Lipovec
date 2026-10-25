# Separate React SPA frontend and Django REST API backend

## Context and Problem Statement

Retroteka is used in two settings: at home on a computer, where a collector organises collections, and at a game fair on a phone, where they quickly check whether they already own a game and what it is worth (US-10). Several screens are interactive: search with a platform filter and "In collection" badges, an add-to-collection modal, a price chart, collection filters with removable chips and a multi-step CSV import preview. At the same time, the rules about who may see and change what (purchase prices only for the owner, hidden collections, moderator actions) must hold no matter which screen a request comes from.

How should the user interface and the application logic be split?

## Decision Drivers

* All business rules and role checks must be enforced in one place, on the server.
* Interactive screens (search, filters, modal forms, price chart, import preview) should update without reloading the whole page, also on a phone.
* Search and filter state must survive a reload and be shareable as a link (US-04, US-19).
* The frontend and the backend should be developed and tested separately (the API with pytest).

## Considered Options

* Separate React SPA (Vite) and a REST API (Django REST Framework)
* Server-rendered Django templates
* Django templates with HTMX
* Next.js full-stack application

## Decision Outcome

Chosen option: "Separate React SPA and a REST API", because it keeps all logic and permissions in the backend while giving the interactive screens a component-based UI. The frontend contains no business logic: it calls JSON endpoints under `/api/` and shows what the backend returns. Search and filter state is kept in the URL query string with React Router.

### Consequences

* Good, because permissions and validation live only in the API, so every request goes through the same checks.
* Good, because the API can be tested with pytest without a browser, and the UI is built against a stable contract.
* Good, because interactive screens update in place, which matters on a slow phone connection at a fair.
* Bad, because there are two codebases, two dev servers and two build tools.
* Bad, because the frontend and the API run on different origins (`:5173` and `:8000`), so CORS has to be configured and authentication cannot simply use Django's session cookies (see [ADR-0009](0009-jwt-authentication.md)).
* Bad, because some validation is repeated in the frontend for quick feedback; the backend remains the authority.
* Neutral, because pages are not rendered on the server, so public collections are not indexed well by search engines; this is not a requirement.

## Pros and Cons of the Options

### Separate React SPA and a REST API

* Good, because the UI and the logic are clearly separated.
* Good, because React components fit the interactive screens.
* Bad, because of extra setup: CORS, token authentication, two builds.

### Server-rendered Django templates

* Good, because it is the simplest setup: one codebase, one server, sessions and CSRF protection built in.
* Good, because filter state in the URL comes naturally with GET forms.
* Bad, because every filter change, page of results or form error reloads the whole page.
* Bad, because the price chart, the add-to-collection modal and the import preview would need hand-written JavaScript on top anyway.

### Django templates with HTMX

* Good, because parts of a page can be updated without a JavaScript framework.
* Good, because everything stays in one Django project.
* Bad, because HTML templates and application logic end up mixed in the same views.
* Bad, because the more complex screens (price chart, multi-step import with a choice per row) still need separate JavaScript.

### Next.js full-stack application

* Good, because it combines React with server-side rendering in one framework.
* Bad, because it adds a Node.js server, so logic would be split between Node.js and Django, or Django would have to be dropped (see [ADR-0002](0002-django-and-drf-for-backend.md)).
* Bad, because it has more moving parts than the project needs.

## More Information

* Architecture overview: [04 – Arhitektura in tehnološki sklad](../04-arhitektura-in-tehnoloski-sklad.md)
* User stories: [05 – User Stories](../05-uporabniske-zgodbe.md), wireframes: [06 – Wireframes](../06-wireframes.md)
* A native mobile app is out of scope ([02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md)).
* Related: [ADR-0002](0002-django-and-drf-for-backend.md), [ADR-0009](0009-jwt-authentication.md).
