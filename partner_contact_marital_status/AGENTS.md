# partner_contact_marital_status

## Purpose

Adds the marital status of persons to the _Personal Information_ page of contacts.

## Models

- `res.partner.marital.status`: configurable list (`name` translatable, `active`).
  Default records (noupdate): single, married, divorced, widowed.
- `res.partner`: `marital_status_id`.

## Rules

- Partner managers maintain the list (Contacts > Configuration > Marital Status),
  internal users read it.

## Pitfalls

- Licensed AGPL-3 since 20.0 (was OPL-1 in the Himmelblau 19.0 repository).
