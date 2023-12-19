# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    # From V11 to V12
    openupgrade.rename_columns(
        env.cr, {
            'res_partner': [
                ('zip_id', None),
            ]
        }
    )
    openupgrade.remove_tables_fks(env.cr, ['res_better_zip'])
