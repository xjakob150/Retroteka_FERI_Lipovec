# Store the user's role as a single field on the user

## Context and Problem Statement

Retroteka has four roles ([02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md)): guest, collector, moderator and administrator. A guest is a visitor without an account. Every account has exactly one role, and the roles build on each other: a moderator can do everything a collector can, and an administrator everything a moderator can. Most rules are about ownership and visibility, not about models. A collector edits only their own collections, a moderator hides a public collection but cannot edit it, and an administrator changes roles and blocks accounts but does not see passwords or change other users' collections. In the MVP, the administrator manages users in Django admin (feature #11).

How should roles and permissions be modelled?

## Decision Drivers

* Each user has exactly one role.
* Rules are mostly per object (owner vs. others) and cumulative by role.
* A role change must apply from the user's next action (US-23).
* The administrator must be able to manage users in Django admin, and nothing else there.

## Considered Options

* A `role` field with choices on the user
* Django groups and model permissions
* A separate `Role` table with a many-to-many relation to users
* Only Django's `is_staff` and `is_superuser` flags

## Decision Outcome

Chosen option: "A `role` field with choices on the user", because it allows exactly one role per user and keeps permission checks as simple comparisons in DRF permission classes. Details:

* `User.role` is one of `collector`, `moderator` or `admin`; new accounts get `collector` (US-01).
* DRF permission classes check the role and ownership, e.g. "moderator or admin" for hiding a collection and "owner" for editing it.
* `User.save()` sets `is_staff = (role == "admin")`, so administrators can log in to Django admin.
* `createsuperuser` creates an account with `role = "admin"`; it is the only account with `is_superuser`.
* The role is read from the database on every request ([ADR-0009](0009-jwt-authentication.md)), so a change applies immediately.

### Consequences

* Good, because the role is stored in one place, and checks are easy to read and test.
* Good, because changing a role is a single field update.
* Bad, because adding a role or a finer-grained permission requires code changes and a migration.
* Bad, because `is_staff` duplicates information from `role`. It stays in sync only through `save()`; bulk updates with `QuerySet.update()` skip `save()` and must not be used to change roles.
* Bad, because Django admin checks model permissions, not our role. An administrator without `is_superuser` has no model permissions, so the user admin must override its permission methods to allow users with `role == "admin"`, and other models must stay closed to them.

### Confirmation

Tests for the permission classes: a collector cannot hide a collection, a moderator cannot edit another user's collection, and an administrator can open the user admin but cannot edit collections there.

## Pros and Cons of the Options

### A `role` field with choices on the user

* Good, because there is exactly one role, checks are simple and changes take effect immediately.
* Bad, because `is_staff` has to be kept in sync and Django admin permissions have to be overridden.

### Django groups and model permissions

* Good, because they are built into Django and Django admin, and can be configured without code.
* Bad, because a user can be in several groups, so "exactly one role" is not guaranteed.
* Bad, because model permissions are per model (add, change, delete, view), not per object; rules like "only the owner may edit" still need custom permission classes.

### A separate `Role` table (many-to-many)

* Good, because new roles can be added as data.
* Bad, because many-to-many allows several roles per user, which the domain does not have, and every check needs an extra join.

### Only `is_staff` and `is_superuser`

* Good, because no new field is needed.
* Bad, because two flags cannot clearly express three roles.
* Bad, because `is_superuser` gives full access in Django admin, including other users' collections, which administrators must not change.

## More Information

* "Uporabniške vloge" in [02 – Funkcionalnosti in obseg](../02-funkcionalnosti-in-obseg.md); "Vloga je polje na uporabniku" in [03 – Podatkovni model](../03-podatkovni-model.md)
* Related: [ADR-0002](0002-django-and-drf-for-backend.md), [ADR-0009](0009-jwt-authentication.md).
