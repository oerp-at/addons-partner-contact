# Copyright 2026 Weboffice <https://www.weboffice.at>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """Catch up on 19.0.1.0.0/pre-migration.py for databases that skipped it.

    The 19.0 simplification dropped the SQL views and renamed the relation type
    fields in a script bound to 19.0.1.0.0. Databases that ran their own 19.0 port
    of the old module are already at 19.0.1.0.0, so that script never ran for them
    and they still carry the old views and column names. Every step is guarded, so
    on a database that ran the 19.0 scripts this is a no-op.
    """
    logger.info("Delete obsolete SQL views, if any")
    env.cr.execute("DROP VIEW IF EXISTS res_partner_relation_all;")
    env.cr.execute("DROP VIEW IF EXISTS res_partner_relation_type_selection;")
    model_name = "res.partner.relation.type"
    table_name = "res_partner_relation_type"
    renames = [
        (model_name, table_name, old, new)
        for old, new in (
            ("contact_type_left", "left_partner_type"),
            ("contact_type_right", "right_partner_type"),
            ("partner_category_left", "left_partner_category_id"),
            ("partner_category_right", "right_partner_category_id"),
        )
        if openupgrade.column_exists(env.cr, table_name, old)
        and not openupgrade.column_exists(env.cr, table_name, new)
    ]
    if renames:
        logger.info("Renaming res_partner_relation_type fields")
        openupgrade.rename_fields(env, renames)
