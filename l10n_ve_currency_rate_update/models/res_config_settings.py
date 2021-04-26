from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_rates_auto_update = fields.Boolean(
        'Automatic Currency Rates',
        related='company_id.currency_rates_auto_update',
        readonly=False,
        help='Enable regular automatic currency rates updates'
    )
