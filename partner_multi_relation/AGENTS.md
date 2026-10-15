# partner_multi_relation

## Purpose

Typed relations between partners (e.g. "is employer of" / "is employee of"), with
optional restrictions on partner type and category per side, validity dates, and
searching partners by their relations.

## Models

- `res.partner.relation.type`: `name` / `name_inverse` (left->right and right->left
  wording), `left_partner_type` / `right_partner_type` (`c` organisation, `p` person,
  empty = any), `left_partner_category_id` / `right_partner_category_id`, `allow_self`,
  `is_symmetric`, `handle_invalid_onchange` (restrict / ignore / end / delete, applied
  to existing relations when the restrictions of a type change).
- `res.partner.relation`: one stored row per relation (`left_partner_id`, `type_id`,
  `right_partner_id`, `date_start`, `date_end`, `active`). `this_partner_id`,
  `other_partner_id` and `type_id_display` are computed from the context key
  `current_partner_id`, so a relation reads from the point of view of the partner it is
  opened from. `*_domain` fields are Json domains for the form.
- `res.partner`: `relation_left_ids` / `relation_right_ids`, `relation_count`,
  `action_view_relations`, and non-stored `search_relation_*` fields that only exist to
  be searched on.

## Rules

- Partner type `c`/`p` is checked against `res.partner.is_company`. Since 20.0 that is
  core's computed rule (own commercial partner with a VAT, refined by localizations), so
  a company without a VAT counts as a person. The module deliberately follows core; to
  keep a manual person/company choice, install `partner_company_manual`.
- `search()` on `res.partner` adds "valid today" and "active relation" conditions when a
  `search_relation_*` field is used without an explicit date.
- The 19.0 simplification replaced the SQL views `res_partner_relation_all` and
  `res_partner_relation_type_selection` by the plain `res.partner.relation` model and
  renamed the type fields (`contact_type_left` -> `left_partner_type`,
  `partner_category_left` -> `left_partner_category_id`, same for right).

## Pitfalls

- `migrations/20.0.1.0.0` repeats the 19.0 steps (drop views, rename fields, clear menu
  actions pointing at removed actions/models) guarded, for databases that ran their own
  19.0 port and are already at 19.0.1.0.0 without the 19.0 scripts. Without them the
  type restrictions are silently emptied and the backend menu fails to load. The
  post-migration logs how many relations no longer match their type's partner type.
- Tests and demo data create companies with a VAT; `is_company` in create values is
  ignored by core since 20.0.
- An empty Json domain field reads back as `False`, not `[]`: normalize with
  `Domain(value or [])`.
- Odoo 20's contacts hierarchy view follows `parent_id`/`child_ids` only; relations are
  an n:m graph and are not shown there (no hierarchy support by decision).
