# partner_contact_personal_information_page

## Purpose

Adds an empty "Personal Information" page to the partner form. Other modules
(`partner_contact_birthdate`, `partner_contact_nationality`, ...) put their person
fields into it.

## Views

- `personal_information` inherits `base.view_partner_form`, page
  `personal_information_page` with group `personal_information_group`, placed after
  `internal_notes`, `invisible="is_company"`.
- Dependent modules add fields with `//group[@name='personal_information_group']` and
  declare the same view record in their own module if they must work without this
  module.

## Pitfalls

- 20.0: `is_company` is computed from the VAT; companies without VAT show the page.
