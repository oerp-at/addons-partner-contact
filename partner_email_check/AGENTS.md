# partner_email_check

## Purpose

Validates and normalizes partner email addresses with the `email-validator` library and
can forbid duplicate addresses. All checks are company settings (Settings > General
Settings > Email validation).

## Models

- `res.company`: `partner_email_check_syntax` (default on),
  `partner_email_check_filter_duplicates`, `partner_email_check_check_deliverability`.
- `res.config.settings`: related fields; enabling deliverability also enables syntax.
- `res.partner`: `create`/`write` run `email_check`; constraint `_check_email_unique`;
  `copy_data` drops the email when duplicates are filtered.

## Rules

- Syntax check on: every comma-separated address is validated and stored normalized
  (lowercase, punycode domains decoded to Unicode, e.g. `xn--xample-9ua.com` ->
  `éxample.com`).
- Duplicate filter on: only one address per partner, and no other active partner may
  have the same address (archived partners are not checked).
- Deliverability check does a DNS lookup of the domain.

## Pitfalls

- The checks follow `self.env.company`, not the partner's company.
- Deliverability needs DNS; in offline test or import runs keep it off.
- Imports with invalid addresses fail with a `ValidationError` while syntax check is on.
