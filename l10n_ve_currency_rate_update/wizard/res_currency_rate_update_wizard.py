from odoo import fields, models, api


class ResCurrencyRateUpdateWizard(models.TransientModel):
    _name = 'res.currency.rate.update.wizard'
    _description = 'Currency Rate Update Wizard'

    date_from = fields.Date(
        'Start Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        'End Date',
        required=True,
        default=fields.Date.context_today,
    )
    provider_ids = fields.Many2many(
        'res.currency.rate.provider',
        'wizard_id',
        'provider_id',
        string='Providers'
    )

    def action_update(self):

        self.ensure_one()
        self.provider_ids._update(self.date_from, self.date_to)

        return {'type': 'ir.actions.act_window_close'}
