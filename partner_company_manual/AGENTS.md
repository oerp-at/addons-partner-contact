# partner_company_manual

## Purpose

Restores the manual person/company toggle on partners that Odoo removed in 20.0. Since
20.0 `is_company` is computed (own commercial partner AND a VAT, refined by
localizations), so companies without VAT (small businesses, parishes, public offices)
would become persons.

## Models

- `res.partner`:
  - `is_company_manual` (Selection person/company, stored, copied): the user's choice.
    Empty means "automatic" (standard Odoo rule).
  - `company_type` (Selection, not stored, compute + inverse): interface field for the
    radio, like up to 19.0. Do not use it in business logic, use `is_company`.
  - `_compute_is_company`: runs the standard (and localization) rule, then the manual
    choice wins where it is set. Adds `is_company_manual` to the dependencies.

## Rules

- Manual choice beats the VAT: a manual company stays a company without VAT, a manual
  person stays a person with VAT, also when the VAT changes later.
- Writing `is_company` in create/write (API up to 19.0, e.g. EDI import, portal, custom
  code) sets `is_company_manual`; `is_company` stays in the vals so other overrides
  (e.g. `partner_firstname`) still see it.
- Changing the radio in a form switches `is_company` immediately (onchange), so views
  depending on `is_company` react live.
- `post_init_hook` freezes the current state of all existing partners into
  `is_company_manual` (SQL, after `flush_all`).

## Pitfalls

- The hook only preserves what `is_company` contains at install time. If the Odoo
  upgrade from 19.0 already recomputed `is_company` from the VAT, install this module in
  the upgraded database before users edit partners and check companies without VAT.
- Main form: the radio sits in the header group before the `name` label
  (`//sheet/div/group/label[@for='name']`); simple form: before the `h1`, debug mode
  only (as in 19.0).
- With `partner_firstname` the name field is read-only for persons: set the type first,
  then the name (also in `Form` tests).
