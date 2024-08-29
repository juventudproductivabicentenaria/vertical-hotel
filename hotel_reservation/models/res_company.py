# -*- coding: utf-8 -*-

from odoo import fields, models, api
import pytz

_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]


def _tz_get(self):
    return _tzs


class ResCompany(models.Model):
    _inherit = 'res.company'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Hotel',
    )
    
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Lista de precios',
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        related='company_id.warehouse_id',
        readonly=False,
        required=True,
        help='Hotel setup for website',
        string='Hotel',
    )

    pricelist_id = fields.Many2one(
        'product.pricelist',
        related='company_id.pricelist_id',
        readonly=False,
        required=True,
        string='Lista de precios',
    )


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    user_id = fields.Many2one('res.users')
    tz = fields.Selection(_tz_get, string='Timezone', default=lambda self: self._context.get('tz'),
                          required=True,
                          help="This field is used in order to define in which timezone the resources will work.")
