# Use Docker Compose for local development

## Context and Problem Statement

The application consists of three services: the React frontend (Vite dev server), the Django backend and a PostgreSQL database. The backend also needs secret keys for IGDB and eBay. Anyone who runs the project, whether the developer on a new machine or a reviewer of the assignment, should get it running quickly and with the same versions of Python, Node.js and PostgreSQL.

How should the project be set up and started locally?

## Decision Drivers

* All services start with one command.
* Same versions of Python, Node.js and PostgreSQL on every machine.
* No local PostgreSQL installation.
* Secret keys in a `.env` file that is not committed.

## Considered Options

* Docker Compose for all three services
* Manual installation of Python, Node.js and PostgreSQL
* Only PostgreSQL in Docker, with the frontend and backend running directly on the host

## Decision Outcome

Chosen option: "Docker Compose for all three services", because it is the only option that starts the whole application with one command in the same environment on every machine. `docker-compose.yml` defines the services `frontend`, `backend` and `db`. Keys are read from `.env`, for which `.env.example` is the template. This decision covers local development only; production deployment will be decided in a separate ADR.

### Consequences

* Good, because `docker compose up --build` starts everything, and a reviewer only needs Docker installed.
* Good, because development and tests use the same PostgreSQL version ([ADR-0003](0003-postgresql-as-database.md)).
* Good, because secret keys stay out of the repository.
* Bad, because Docker is required, and hot reload through bind-mounted files can be slower than running natively.
* Bad, because Django commands run through `docker compose exec backend ...`, and changing dependencies requires rebuilding the image.

### Confirmation

From a clean clone, the steps from "Lokalni zagon" in `04-arhitektura-in-tehnoloski-sklad.md` (`cp .env.example .env`, `docker compose up --build`, `migrate`, `loaddata platforms`) bring up the frontend on http://localhost:5173 and the API on http://localhost:8000/api/.

## Pros and Cons of the Options

### Docker Compose for all three services

* Good, because one command starts an identical environment everywhere.
* Bad, because of Docker overhead and slower file watching.

### Manual installation of Python, Node.js and PostgreSQL

* Good, because no Docker is needed and hot reload is fastest.
* Bad, because every machine needs the right versions installed and configured by hand, which leads to "works on my machine" problems.
* Bad, because a reviewer would have to set up PostgreSQL before trying the project.

### Only PostgreSQL in Docker

* Good, because the database starts easily while the apps run natively with fast reload.
* Bad, because Python and Node.js versions can still differ between machines.
* Bad, because starting the project takes several commands in separate terminals.

## More Information

* "Lokalni zagon" in [04 – Arhitektura in tehnološki sklad](../04-arhitektura-in-tehnoloski-sklad.md)
* Related: [ADR-0003](0003-postgresql-as-database.md), [ADR-0008](0008-only-backend-calls-external-apis.md) (keys are used only by the backend).
