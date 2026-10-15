When the user enters a postal code (and optionally a street) on a contact, this
module fills **country**, **city** and **state** from official postal-code
directories. The country is chosen automatically from the postal-code length:

- **4 digits** -> **Austria**, using the postal-code table published as open
  data by [RTR](https://data.rtr.at/) (the Austrian Post / regulator registry).
  It lists one canonical delivery town (Bestimmungsort) per postal code, so
  Austrian codes are never ambiguous.
- **5 digits** -> **Germany**, using the OpenStreetMap-derived street list
  published by [openPLZ](https://github.com/openpotato/openplzapi.data).

Each country is switched on independently under **Settings > General Settings >
Integrations**. Once enabled, an **Import ZIP Directory** button downloads the
source, reduces it to the distinct postal-code/city combinations and stores them
in the `country.zip.city` model. While a country is disabled, or before its
directory has been imported, nothing is autofilled for that country.

Address resolution works as follows:

1. The postal code is looked up in the local directory. If it maps to a single
   city, that city (and its state) is used directly. Austria always takes this
   path, because the RTR table is unambiguous.
2. For **Germany** only, if a postal code is shared by several cities and a
   **street** is present, the [OpenPLZ API](https://openplzapi.org/) full-text
   search is queried with the street and postal code (the house number is
   trimmed first) to pin down the correct city, which is then matched back onto
   a directory row.
3. If OpenPLZ cannot be reached or does not resolve to a single city, the most
   common city for that postal code is used as a deterministic best guess. The
   **state** is derived the same way, which also covers postal codes that
   straddle two federal states.
