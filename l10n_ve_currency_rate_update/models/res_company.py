from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_rates_auto_update = fields.Boolean(
        'Automatic Currency Rates',
        default=True,
        help='Enable regular automatic currency rates updates',
        oldname='auto_currency_up'
    )
