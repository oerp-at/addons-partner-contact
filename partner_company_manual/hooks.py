# Copyright 2026 Weboffice IT und Marketing GmbH & CoKG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    """Freeze the current person/company state of all existing partners.

    Without this, partners that are companies but have no VAT (e.g. data migrated
    from 19.0) would turn into persons on the next recomputation of is_company.
    """
    env.flush_all()
    env.cr.execute(
        """
        UPDATE res_partner
           SET is_company_manual = CASE WHEN is_company THEN 'company'
                                        ELSE 'person' END
         WHERE is_company_manual IS NULL
        """
    )
