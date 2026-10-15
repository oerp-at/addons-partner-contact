1. Go to **Settings > General Settings > Integrations** and enable
   **Address Autofill (AT)** and/or **Address Autofill (DE)**.
2. Click **Import ZIP Directory (AT/DE)**. The source is downloaded and imported
   in one go, replacing that country's existing data. The Austrian table is
   small; the German import takes a moment because of the larger source file.
   Re-running an import simply refreshes the data.
3. On a partner form, enter an **Austrian 4-digit** or **German 5-digit ZIP**
   (and optionally a street) and leave the field. **Country** is set
   accordingly, and **City** and **State** are filled automatically.

Austrian postal codes always resolve to a single city. For Germany, if a code is
shared by several cities, a street is used together with the OpenPLZ full-text
search to pin down the exact one; without a street (or when OpenPLZ cannot
resolve it) the most common city for the postal code is used. Codes that are not
exactly 4 or 5 digits, or that have no match, leave the address unchanged. While
a country is disabled, or before its directory has been imported, nothing is
autofilled for that country.
