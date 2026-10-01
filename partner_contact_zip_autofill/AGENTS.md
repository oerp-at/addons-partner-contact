# partner_contact_zip_autofill

## Purpose

Fills country, city and state of a contact from the postal code (Austria and Germany),
based on a local postal-code directory.

## Models

- `country.zip.city`: local directory (`zip`, `city`, `municipality_code`, `state_id`,
  `country_id` related). Filled by import actions in the settings.
- `res.partner`: onchange on `zip`/`street` (`_onchange_zip_autofill`).
- `res.config.settings`: switches per country (`partner_contact_zip_autofill.at_enabled`
  / `de_enabled`, booleans) and import buttons.

## Rules

- Country by postal-code length: 4 digits = AT, 5 digits = DE, only if switched on.
- AT: RTR table, one delivery town per postal code, never calls an API.
- DE: OpenStreetMap street list; an ambiguous postal code is resolved via the OpenPLZ
  full-text search with the street (2 s timeout), otherwise the most common city wins.
- An import replaces all rows of the country in one delete + bulk insert, guarded by a
  PostgreSQL advisory lock.

## Pitfalls

- 20.0: config parameters are read with `get_bool`; in tests set them with
  `set_bool(key, True)`, never with the string `"False"` (truthy).
- Imports download from the internet (DE file ~55 MB); tests mock `requests.get` and
  `fetch_fulltext`.
