# partner_contact_denomination

## Purpose

Adds the religious denomination of persons to the _Personal Information_ page of
contacts.

## Models

- `res.partner.denomination`: configurable list (`name` translatable, `active`). Default
  records (noupdate): Roman Catholic, Protestant, without denomination.
- `res.partner`: `denomination_id`.

## Rules

- Partner managers maintain the list (Contacts > Configuration > Denominations),
  internal users read it.

## Pitfalls

- The default record names are stored in German short form ("Röm.-kath.", "Evang.").
