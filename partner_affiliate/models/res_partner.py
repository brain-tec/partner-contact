# -*- coding: utf-8 -*-
# Copyright 2012 Camptocamp SA - Yannick Vaucher
# Copyright 2018 brain-tec AG - Raul Martin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResPartner(models.Model):
    """Add relation affiliate_ids."""
    _inherit = "res.partner"

    type = fields.Selection(selection_add=[('affiliate', 'Affiliate')])

    # force "active_test" domain to bypass _search() override
    child_ids = fields.One2many('res.partner', 'parent_id',
                                string='Contacts',
                                domain=[('active', '=', True),
                                        ('is_company', '=', False)])

    # force "active_test" domain to bypass _search() override
    affiliate_ids = fields.One2many('res.partner', 'parent_id',
                                    string='Affiliates',
                                    domain=[('active', '=', True),
                                            ('is_company', '=', True)])

    def get_original_address(self):
        def convert(value):
            return value.id if isinstance(value, models.BaseModel) else value

        result = {'value': {key: convert(self[key])
                            for key in self._address_fields()}}

        return result

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        # Keep the original address info to set it back if its a company.
        original_address = self.get_original_address()

        new_partner = super(ResPartner, self).onchange_parent_id()

        # When the affiliate is a company, we must set back its address
        # because the super call changes its address by the new parent address.
        # In addition, the type must be set to affiliate instead of contact.
        if self.is_company:
            new_partner.update(original_address)
            new_partner['value'].update({'type': 'affiliate'})

        return new_partner

    @api.multi
    def write(self, values):
        # In case of a removal of an affiliate, the affiliate must be
        # 'un-linked' instead of removed from the database.
        #
        # By default, calls the write with '2' because affiliate_ids is a O2M
        # to res_partner.parent_id which have attribute ondelete='cascade'.
        # As we do not want to break the core behaviour for other features,
        # here we are changing the '2' (DELETE) for a '3' (UNLINK)
        if 'affiliate_ids' in values:
            for affiliate in values['affiliate_ids']:
                if affiliate[0] == 2:
                    affiliate[0] = 3

        return super(ResPartner, self).write(values)
