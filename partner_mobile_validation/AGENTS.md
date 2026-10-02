# partner_mobile_validation

## Purpose

Glue module between core `phone_validation` and OCA `partner_mobile` (auto_install).
Makes the phone widget of `phone` and `mobile` on partners display the INTERNATIONAL
format and dial the E164 number, each of its own field. None of the numbers is a main
number.

## Models

- `res.partner`:
  - `mobile_sanitized`, `mobile_formatted` (computed, not stored): companion fields of
    `mobile`. The phone widget finds them by name (`<fname>_sanitized/_formatted`).
  - `phone_own_sanitized`, `phone_own_formatted` (computed, not stored): companion
    fields of `phone`, set on the phone widgets via `options` `dial_field` /
    `formatted_field`.

## Rules

- Since 20.0, core keeps the raw number (no reformat onchange anymore); formatting is
  only for display/dialing. Do not reintroduce an onchange that rewrites `mobile`.
- `phone_formatted`/`phone_sanitized` of `mail.thread.phone` hold the first valid number
  of `_phone_get_number_fields()` (`mobile` before `phone`). They stay unchanged because
  SMS mass mailing, blacklist and search rely on them; only the widgets of `phone` are
  pointed to `phone_own_*`.
- SMS uses the clicked field (`number_field_name`), WhatsApp/VoIP use the widget's
  `dialNumber`, so they follow the companion fields.

## Views

- Partner form (incl. inline contact form), simple form, list, kanban: companion fields
  loaded invisibly, `phone` widget options point to `phone_own_*`, `mobile` gets the
  phone widget in list and kanban.

## Pitfalls

- Companion fields must be in the view, otherwise the widget falls back to the raw
  value. New views showing `phone` with the phone widget on partners need the same
  `options` and invisible fields.
- The simple form keeps core's `'enable_sms': false` in the replaced `options`.
