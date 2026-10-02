# Copyright 2026 Weboffice <https://www.weboffice.at>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

logger = logging.getLogger(__name__)


def _clear_dangling_menu_actions(env):
    """Catch up on 19.0.1.1.2/post-migration.py for databases that skipped it.

    Databases coming from older versions may still have ``menu_res_partner_relation``
    pointing at ``action_res_partner_relation_all``. That action targets the removed
    ``res.partner.relation.all`` model and is deleted at the end of this update, after
    this script, so the action may still exist here. Clear any act_window action of
    this module's menus whose record is gone or whose model is no longer in the
    registry; otherwise ``/web/webclient/load_menus`` fails and the backend renders
    blank.
    """
    env.cr.execute(
        """
        SELECT menu.id, action.id, action.res_model
          FROM ir_ui_menu AS menu
          JOIN ir_model_data AS data
            ON data.model = 'ir.ui.menu'
           AND data.res_id = menu.id
           AND data.module = 'partner_multi_relation'
     LEFT JOIN ir_act_window AS action
            ON action.id = split_part(menu.action, ',', 2)::integer
         WHERE menu.action LIKE 'ir.actions.act_window,%%'
        """
    )
    menu_ids = [
        menu_id
        for menu_id, action_id, res_model in env.cr.fetchall()
        if not action_id or res_model not in env
    ]
    if menu_ids:
        openupgrade.logged_query(
            env.cr,
            "UPDATE ir_ui_menu SET action = NULL WHERE id IN %s",
            (tuple(menu_ids),),
        )


def _warn_partner_type_mismatch(env):
    """Report relations whose partners no longer match the relation type.

    Since 20.0 ``res.partner.is_company`` is computed (own commercial partner with
    a VAT). Companies without a VAT are persons now, so relations on types limited
    to companies or persons may no longer pass the checks. They are kept as they
    are, but editing them will fail until the partner or the type is fixed.
    """
    env.cr.execute(
        """
        SELECT count(*)
          FROM res_partner_relation AS rel
          JOIN res_partner_relation_type AS rtype ON rtype.id = rel.type_id
          JOIN res_partner AS lp ON lp.id = rel.left_partner_id
          JOIN res_partner AS rp ON rp.id = rel.right_partner_id
         WHERE (rtype.left_partner_type = 'c' AND NOT coalesce(lp.is_company, FALSE))
            OR (rtype.left_partner_type = 'p' AND coalesce(lp.is_company, FALSE))
            OR (rtype.right_partner_type = 'c' AND NOT coalesce(rp.is_company, FALSE))
            OR (rtype.right_partner_type = 'p' AND coalesce(rp.is_company, FALSE))
        """
    )
    count = env.cr.fetchone()[0]
    if count:
        logger.warning(
            "%s partner relation(s) no longer match the partner type of their "
            "relation type, since is_company is computed from the VAT in 20.0. "
            "Review them before editing.",
            count,
        )


@openupgrade.migrate()
def migrate(env, version):
    _clear_dangling_menu_actions(env)
    _warn_partner_type_mismatch(env)
