# partner_contact_job_position

## Purpose

Adds a categorized job position (selectable list) to person contacts, next to the free
text field `function`.

## Models

- `res.partner.job_position`: configurable list (`name`, translatable).
- `res.partner`: `job_position_id`; partner form and search view (group by job position)
  for persons only (`is_company`).

## Pitfalls

- 20.0: `is_company` is computed from the VAT; with `partner_company_manual` it follows
  the person/company toggle again.
- Himmelblau renames the labels "Job position" to "Job"; that wording belongs in a
  Himmelblau module or translation, not in this module.
