On the contact form choose *Person* or *Company* with the toggle above the name.

- A chosen value is kept, also when the VAT number changes later.
- On installation the current person/company state of all existing partners is
  stored as manual choice, so nothing changes for existing data.
- Code that still writes `is_company` (API up to 19.0) sets the manual choice.
