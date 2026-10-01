# partner_firstname

## Purpose

Splits the name of person contacts (and users) into `firstname` and `lastname`. For
persons `name` becomes a stored computed field built from the parts; for companies the
full name is kept in `lastname`.

## Models

- `firstname.mixin` (abstract): `firstname_required`, `lastname_required`,
  `form_has_lastname_first`, name order helpers (`_get_names_order`,
  `_get_computed_name`, `_get_inverse_name`, `_get_whitespace_cleaned_name`).
- `res.partner`: `firstname`, `lastname`; `name` is computed + inverse
  (`_inverse_name_after_cleaning_whitespace`), `required=False`.
- `res.users`: same mixin, names delegated to the partner.
- `res.config.settings`: name order (`partner_names_order`: first_last, last_first,
  last_first_comma) and required fields (`partner_firstname.required_fields`), stored as
  `ir.config_parameter`; "recalculate names" action.

## Rules

- A partner is split only if it is a person (`not is_company`) and `type == 'contact'`.
- At least one of firstname/lastname must be set, otherwise `EmptyNamesError`.
- `create()` decides company vs. person from the vals via `_is_company_from_vals()`:
  explicit `is_company`, else a virtual record (`self.new`) with `vat`/`parent_id`.

## Pitfalls

- 20.0: there is no `company_type` anymore. `is_company` is computed and stored: own
  commercial partner AND a valid VAT (`has_vat`). Companies without VAT are persons in
  standard 20.0 and their names get split.
- 20.0: partner forms have one `name` field in the `h1` (no `company`/`individual` field
  ids); the simple form uses `field[@id='contact']`.
- 20.0: `ir.config_parameter.get_param/set_param` are gone, use `get_str`/`set_str` (or
  `get_bool`, `get_int`, ...).
- Form tests must set a VAT to get a company (`partner_form.vat = "BE0477472701"`).
