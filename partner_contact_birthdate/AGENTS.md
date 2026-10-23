# partner_contact_birthdate

## Purpose

Adds the birthdate and the computed age of persons to the _Personal Information_ page of
contacts.

## Models

- `res.partner`: `birthdate_date` (Date), `age` (Integer, computed, not stored).

## Rules

- `age` is the full years from `birthdate_date` until today; other modules may extend
  `_compute_age` (e.g. `partner_contact_deathdate` stops it at the date of death).

- `birthdate_date` must not be in the future (`_check_birthdate_not_in_future`, user's today
  via `context_today`). Existing records are only checked when the birthdate
  is written.

## Pitfalls

- `age` is not stored: it cannot be searched or grouped, and it changes daily.
