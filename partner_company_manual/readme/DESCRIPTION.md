Since Odoo 20.0 a partner is a company only if it is its own commercial entity
and has a VAT number. The person/company toggle of earlier versions is gone, so
companies without VAT (small businesses, parishes, public offices, ...) become
persons.

This module brings back the manual person/company toggle on the partner form.
The toggle wins over the VAT rule; partners without a manual choice keep the
standard Odoo behaviour.
