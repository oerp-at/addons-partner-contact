# partner_contact_deathdate

## Purpose

Adds the date of death next to the birthdate on the _Personal Information_ page of
contacts (funeral business).

## Models

- `res.partner`: `deathdate` (Date); extends `_compute_age` of
  `partner_contact_birthdate`.

## Rules

- The age of a deceased person is computed from birthdate to date of death.
- Constraint: the date of death is neither before the birthdate nor in the future.

## Pitfalls

- The view inherits `partner_contact_birthdate.view_partner_form` and places the field
  after `birthdate_date`; a renamed birthdate view breaks this module.
