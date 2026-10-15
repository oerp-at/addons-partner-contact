# partner_contact_birthplace

## Purpose

Adds the place of birth of persons to the _Personal Information_ page of contacts.

## Models

- `res.partner`: `birth_city`, `birth_zip` (Char), `birth_state_id`
  (`res.country.state`), `birth_country_id` (`res.country`).

## Pitfalls

- Pure data fields, no logic and no tests.
