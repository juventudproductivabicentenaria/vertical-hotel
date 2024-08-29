# Copyright 2016 GRAP (http://www.grap.coop)
#        Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import re
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_son = fields.Boolean(string="Hijo (a) Sin C.I.", required=False)
    vat = fields.Char(string="Cedula de identidad", required=False)
    property_account_receivable_id = fields.Many2one('account.account', required=False)
    property_account_payable_id = fields.Many2one('account.account', required=False)
    institution_id = fields.Many2one(
        "hotel.institution", "Intitucion/Empresa", required=False,
    )

    # @api.onchange('vat')
    # def _check_field_vat(self):
    #     regex = r'^[VE]-\d{1,8}$'
    #     for record in self:
    #         if record.vat and not re.match(regex, record.vat):
    #             raise UserError(_("Follow the format V-12345678 o E-12345678, please"))
            

    @api.constrains('vat')
    def _check_already_vat(self):
        if self.vat:
            value = self.search([('vat', 'ilike', self.vat), ('id', '<>', self.id)])
            if (value):
                raise ValidationError(_("Ya existe un registro con este Cedula de identidad/CI: " + str(self.vat)))
            

class HotelInstitucion(models.Model):
    _name = "hotel.institution"

    name =  fields.Char("Intitucion/Empresa", required=True)

    