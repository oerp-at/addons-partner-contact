# partner_contact_birthdate

## Purpose

Adds the birthdate and the computed age of persons to the _Personal Information_ page of
contacts.

## Models

- `res.partner`: `birthdate_date` (Date), `age` (Integer, computed, not stored).

## Rules

- `age` is the full years from `birthdate_date` until today; other modules may extend
  `_compute_age` (e.g. `partner_contact_deathdate` stops it at the date of death).

## Pitfalls

- `age` is not stored: it cannot be searched or grouped, and it changes daily.
