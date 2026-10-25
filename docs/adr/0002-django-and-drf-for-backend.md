# Use Django and Django REST Framework for the backend

## Context and Problem Statement

The backend holds all business logic: users with roles, collections and items, the clients for IGDB and eBay, and the REST API for the frontend ([ADR-0001](0001-separate-react-spa-and-rest-api.md)). The project is built by one developer. In the MVP an administrator must be able to manage users (assign roles, block accounts) before the in-app user management page exists (feature #11).

Which backend framework lets one developer build this fastest and most reliably?

## Decision Drivers

* Python is the developer's strongest language, and the developer has experience with Flask.
* Users, password hashing, permissions, an ORM and schema migrations should be available without assembling them from separate packages.
* An admin interface for managing users in the MVP, without building one.
* Good support for a REST API: serializers, permission classes, throttling and JWT.

## Considered Options

* Django + Django REST Framework (DRF)
* Flask with extensions
* FastAPI
* Node.js + Express
* Spring Boot

## Decision Outcome

Chosen option: "Django + Django REST Framework", because it is a Python framework that ships users, authentication, an ORM, migrations and an admin interface out of the box, and DRF adds serializers, permission classes and throttling on top. Experience with Flask carries over (Python, views that handle a request and return a response), while Django removes the need to choose and wire together extensions. The project is split into the Django apps `users`, `collection`, `games` (IGDB client) and `pricing` (eBay client).

### Consequences

* Good, because user management in the MVP is done in Django admin, with no extra frontend work.
* Good, because the data model in `03-podatkovni-model.md` maps directly to Django models, and migrations keep the schema in version control.
* Good, because DRF permission classes are a natural place for role and ownership checks ([ADR-0011](0011-user-role-as-single-field.md)), and `djangorestframework-simplejwt` provides JWT ([ADR-0009](0009-jwt-authentication.md)).
* Bad, because Django and DRF have a learning curve coming from Flask (class-based views, serializers, settings conventions).
* Bad, because Django views are synchronous by default, so calls to IGDB and eBay block a worker while they wait (see [ADR-0012](0012-ebay-browse-api-for-estimated-prices.md)).
* Neutral, because parts of Django (templates, login pages with sessions) stay unused, since the UI is a separate SPA.

## Pros and Cons of the Options

### Django + Django REST Framework

* Good, because "batteries included": authentication, ORM, migrations, admin.
* Good, because it is Python, the developer's strongest language.
* Bad, because it has more conventions to learn than Flask.

### Flask with extensions

* Good, because the developer already knows it.
* Good, because it is small and flexible.
* Bad, because the ORM, migrations, authentication, JWT and admin come from separate extensions (Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Admin) that have to be chosen, configured and kept compatible by hand.

### FastAPI

* Good, because it is fast, asynchronous and generates OpenAPI documentation.
* Bad, because there is no built-in ORM, migrations, user model or admin; all of it has to be added (e.g. SQLAlchemy and Alembic) or written.

### Node.js + Express

* Good, because the same language (JavaScript) on the frontend and the backend.
* Bad, because the developer is less proficient in server-side JavaScript than in Python.
* Bad, because, like Flask, everything beyond routing comes from separate packages.

### Spring Boot

* Good, because it is mature and strongly typed, with Spring Security for authentication.
* Bad, because Java is not the developer's strongest language, and the setup is heavier than the project needs.

## More Information

* [04 – Arhitektura in tehnološki sklad](../04-arhitektura-in-tehnoloski-sklad.md)
* Feature #11 (in-app user management) in [02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md)
* Related: [ADR-0001](0001-separate-react-spa-and-rest-api.md), [ADR-0003](0003-postgresql-as-database.md).
