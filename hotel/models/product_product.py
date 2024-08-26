# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    isroom = fields.Boolean("Is Room")
    iscategid = fields.Boolean("Is Categ")
    isservice = fields.Boolean("Is Service")

    default_code = fields.Char('Default Code', copy=False)

    # def _get_default_code(self):
    #     if self.default_code:
    #         return self.default_code
    #     return super(ProductProduct, self)._get_default_code()
