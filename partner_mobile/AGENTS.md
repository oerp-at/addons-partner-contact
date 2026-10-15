# partner_mobile

## Purpose

Restores the `mobile` field on `res.partner`, which Odoo removed in 19.0.

## Models

- `res.partner`: `mobile` (Char).

## Views

- Partner list, form (after the phone row), kanban and simple form.

## Pitfalls

- Pure field module, no logic and no tests. Phone formatting/SMS widgets of core only
  apply to `phone`.
