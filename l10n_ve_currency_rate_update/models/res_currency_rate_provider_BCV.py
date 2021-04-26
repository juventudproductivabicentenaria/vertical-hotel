from collections import defaultdict
from odoo import fields, models, api
from datetime import date, timedelta
import requests
import xlrd


class ResCurrencyRateProviderBCV(models.Model):
    _inherit = 'res.currency.rate.provider'

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != 'BCV':
            return super()._get_supported_currencies()  # pragma: no cover

        # List of currencies obrained from:
        # http://www.bcv.org.ve/sites/default/files/EstadisticasGeneral/2_1_2a21_otrasmonedas.xls
        return \
            [
                'USD', 'JPY', 'BGN', 'CYP', 'CZK', 'DKK', 'EEK', 'GBP',
                'HUF', 'LTL', 'LVL', 'MTL', 'PLN', 'ROL', 'RON', 'SEK',
                'SIT', 'SKK', 'CHF', 'ISK', 'NOK', 'HRK', 'RUB', 'TRL',
                'TRY', 'AUD', 'BRL', 'CAD', 'CNY', 'HKD', 'IDR', 'ILS',
                'INR', 'KRW', 'MXN', 'MYR', 'NZD', 'PHP', 'SGD', 'THB',
                'ZAR', 'EUR', 'ARS', 'BOB', 'COP', 'CLP', 'NIO', 'PEN',
                'DOP', 'TTD', 'UYU', 'ANG', 'TWD', 'JOD', 'VEF'
            ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != 'BCV':
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)

        invert_calculation = False

        if base_currency != 'VEF':
            invert_calculation = True
            if base_currency not in currencies:
                currencies.append(base_currency)

        url = 'http://www.bcv.org.ve/sites/default/files/EstadisticasGeneral/2_1_2a21_otrasmonedas.xls'
        r = requests.get(url)
        workbook = xlrd.open_workbook(file_contents=r.content)
        content = defaultdict(dict)
        date_today = date.today()

        worksheet_date_today = workbook.sheet_by_index(0)
        rows_worksheet_today = worksheet_date_today.nrows

        for rowx, row in enumerate(map(worksheet_date_today.row, range(worksheet_date_today.nrows)), 1):
            if rowx in range(11, 46):
                currency_new = row[1].value
                rate_vef = row[5].value
                rate = row[3].value

                if invert_calculation:
                    if currency_new in currencies:
                        content[date_today.isoformat()][currency_new] = 1.0 / rate
                        if 'USD' in currency_new:
                            content[date_today.isoformat()]['VEF'] = rate_vef
                        else:
                            continue
                else:
                    if currency_new in currencies:
                        if 'USD' in currency_new:
                            content[date_today.isoformat()]['VEF'] = rate_vef

                        if currency_new in ('USD', 'AUD', 'EUR'):
                            content[date_today.isoformat()][currency_new] = 1.0 / rate
                        else:
                            content[date_today.isoformat()][currency_new] = rate

        return content
