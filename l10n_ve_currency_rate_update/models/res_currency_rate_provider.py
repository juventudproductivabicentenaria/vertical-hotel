# import logging
import logging

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from sys import exc_info

_logger = logging.getLogger(__name__)


class ResCurrencyRateProvider(models.Model):
    _name = 'res.currency.rate.provider'
    _description = 'Currency Rates Provider'
    _inherit = ['mail.thread']
    _order = 'name'

    active = fields.Boolean(
        default=True,
    )
    available_currency_ids = fields.Many2many(
        'res.currency',
        'Available Currencies',
        compute='_compute_available_currency_ids',
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=lambda self: self._default_company_id()
    )
    currency_name = fields.Char(
        'Currency Name',
        related='company_id.currency_id.name'
    )
    currency_ids = fields.Many2many(
        'res.currency',
        'provider_id',
        'currency_id',
        string='Currencies',
        required=True,
        help='Currencies to be updated by this provider'
    )
    # currency_id = fields.Many2one(
    #     'res.currency',
    #     'Currencies',
    #     required=True,
    #     help='Currencies to be updated by this provider'
    # )
    interval_number = fields.Integer(
        'Scheduled update interval',
        default=1,
        required=True,
    )
    interval_type = fields.Selection(
        [('days', 'Day(s)'),
         ('weeks', 'Week(s)'),
         ('months', 'Month(s)'),
         ],
        string='Units of scheduled update interval',
        default='days',
        required=True,
    )
    last_successful_run = fields.Date(
        'Last successful update',
    )
    name = fields.Char(
        'Name',
        compute='_compute_name',
        store=True,
    )
    next_run = fields.Date(
        'Next scheduled update',
        default=fields.Date.today,
        required=True,
    )
    service = fields.Selection([(
        'BCV', 'Venezuela Central Bank'
    )],
        'Source Service',
        required=True,
    )
    update_schedule = fields.Char(
        'Update Schedule',
        compute='_compute_update_schedule'
    )

    @api.depends('service')
    def _compute_name(self):
        for provider in self:
            provider.name = list(filter(
                lambda x: x[0] == provider.service,
                self._fields['service'].selection,
            ))[0][1]

    @api.depends('active', 'interval_type', 'interval_number')
    def _compute_update_schedule(self):
        for provider in self:
            if not provider.active:
                provider.update_schedule = _('Inactive')
                continue
            provider.update_schedule = _('%(number)s %(type)s') % {
                'number': provider.interval_number,
                'type': list(filter(
                    lambda x: x[0] == provider.interval_type,
                    self._fields['interval_type'].selection
                ))[0][1],
            }

    @api.model
    def _default_company_id(self):
        return self.env['res.company']._company_default_get()

    @api.depends('service')
    def _compute_available_currency_ids(self):
        currency = self.env['res.currency']

        for provider in self:
            provider.available_currency_ids = currency.search(
                [('name', 'in', provider._get_supported_currencies()
                  )],
            )

    def _get_supported_currencies(self):
        self.ensure_one()
        return []

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        return {}

    def _get_next_run_period(self):
        self.ensure_one()

        if self.interval_type == 'days':
            return relativedelta(days=self.interval_number)
        elif self.interval_type == 'weeks':
            return relativedelta(weeks=self.interval_number)
        elif self.interval_type == 'months':
            return relativedelta(months=self.interval_number)

    def _schedule_next_run(self):
        self.ensure_one()
        self.last_successful_run = self.next_run
        self.next_run = (
                datetime.combine(
                    self.next_run,
                    time.min
                ) + self._get_next_run_period()
        )

    def _process_rate(self, currency, rate):
        self.ensure_one()

        module = self.env['ir.module.module']
        currency_rate_inverted = module.sudo().search([
            ('name', '=', 'currency_rate_inverted'),
            ('state', '=', 'installed')
        ], limit=1)

        if type(rate) is dict:
            inverted = rate.get('inverted', None)
            direct = rate.get('direct', None)
            if inverted is None and direct is None:
                raise UserError(
                    _(
                        'Invalid rate from %(provider)s for'
                        ' %(currency)s : %(rate)s'
                    ) % {
                        'provider': self.name,
                        'currency': currency.name,
                        'rate': rate,
                    }
                )
            elif inverted is None:
                inverted = 1 / direct
            elif direct is None:
                direct = 1 / inverted
        else:
            rate = float(rate)
            direct = rate
            inverted = 1 / rate

        value = direct
        if currency_rate_inverted and \
                currency.with_context(
                    force_company=self.company_id.id
                ).rate_inverted:
            value = inverted

        return value

    def _update(self, date_from, date_to, newest_only=False):

        currency = self.env['res.currency']
        currency_rate = self.env['res.currency.rate']
        is_scheduled = self.env.context.get('scheduled')

        for provider in self:
            try:
                data = provider._obtain_rates(
                    provider.company_id.currency_id.name,
                    provider.currency_ids.mapped('name'),
                    # provider.currency_id.name,
                    date_from,
                    date_to
                ).items()
            except:
                e = exc_info()[1]
                _logger.warning(
                    'Currency Rate Provider "%s" failed to obtain data since'
                    '%s until %s' % (
                        provider.name,
                        date_from,
                        date_to,
                    ),
                    exc_info=True
                )
                provider.message_post(
                    subject=_('Currency Rate Provider Failure'),
                    body=_(
                        'Currency Rate Provider "%s" failed to obtain data'
                        ' since %s until %s:\n%s'
                    ) % (
                             provider.name,
                             date_from,
                             date_to,
                             str(e) if e else _('N/A'),
                         ),
                )
                self.send_error_notification_user()
                continue

            if not data:
                if is_scheduled:
                    provider._schedule_next_run()
                continue
            if newest_only:
                data = [max(
                    data,
                    key=lambda x: fields.Date.from_string(x[0])
                )]

            for content_date, rates in data:
                timestamp = fields.Date.from_string(content_date)
                for currency_name, rate in rates.items():
                    # if currency_name == provider.company_id.currency_id.name:
                    #     continue
                    currency = currency.search([
                        ('name', '=', currency_name)
                    ], limit=1)

                    if not currency:
                        raise UserError(
                            _(
                                'Unknown currency from %(provider)s: %(rate)s'
                            ) % {
                                'provider': provider.name,
                                'rate': rate,
                            }
                        )
                    rate = provider._process_rate(
                        currency,
                        rate
                    )

                    record = currency_rate.search([
                        ('company_id', '=', provider.company_id.id),
                        ('currency_id', '=', currency.id),
                        ('name', '=', timestamp),
                    ], limit=1)
                    if record:
                        record.write({
                            'rate': rate,
                            # 'provider_id': provider.id,
                        })
                    else:
                        record = currency_rate.create({
                            'company_id': provider.company_id.id,
                            'currency_id': currency.id,
                            'name': timestamp,
                            'rate': rate,
                            # 'provider_id': provider.id,
                        })
            if is_scheduled:
                provider._schedule_next_run()

    def _scheduled_update(self):
        _logger.info('Scheduled currency rates update...')

        providers = self.search([
            ('company_id.currency_rates_auto_update', '=', True),
            ('active', '=', True),
            ('next_run', '<=', fields.Date.today()),
        ])
        if providers:
            _logger.info('Scheduled currency rates update of: %s' % ', '.join(providers.mapped('name')))

            for provider in providers.with_context({'scheduled': True}):
                date_from = (
                        provider.last_successful_run + relativedelta(days=1)
                ) if providers.last_successful_run else (
                        provider.next_run - provider._get_next_run_period()
                )
                date_to = provider.next_run
                provider._update(date_from, date_to, newest_only=True)

        _logger.info('Scheduled currency rates update complete.')

    def send_error_notification_user(self):

        self.ensure_one()

        user = self.env.user
        ir_model_data = self.env['ir.model.data']

        try:
            template_id = self.env.ref('l10n_ve_currency_rate_update.email_template_notification_owner')
        except ValueError:
            template_id = False

        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'res.currency.rate.provider',
            'active_model': 'res.currency.rate.provider',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'partner_to': user.sudo()
        })
        try:
            template_id.with_context(ctx).send_mail(self.id, raise_exception=True)
        except:
            pass