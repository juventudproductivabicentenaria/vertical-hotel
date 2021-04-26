# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        price_subtotal *= sign
        if currency:
            if currency != company.currency_id and company.currency_id == self.product_id.currency_id:
                balance = currency._convert(price_subtotal, company.currency_id, company, date)
                return {
                    'amount_currency': price_subtotal,
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                }
            elif currency != company.currency_id and company.currency_id != self.product_id.currency_id:
                if currency != self.product_id.currency_id:
                    price_1 = currency._convert(price_subtotal, company.currency_id, company, date)
                    balance = self.product_id.currency_id._convert(price_1, company.currency_id, company, date)
                    price_2 = company.currency_id._convert(balance, currency, company, date)
                    return {
                        'amount_currency': price_2,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                    }
                else:
                    price = currency._convert(price_subtotal, company.currency_id, company, date)
                    balance = currency._convert(price, company.currency_id, company, date)
                    return {
                        'amount_currency': price,
                        'debit': balance > 0.0 and balance or 0.0,
                        'credit': balance < 0.0 and -balance or 0.0,
                    }
        elif company.currency_id != self.product_id.currency_id:
            balance = self.product_id.currency_id._convert(price_subtotal, company.currency_id, company, date)
            return {
                'amount_currency': 0,
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
            }


        else:
            # Single-currency.
            return {
                'amount_currency': 0.0,
                'debit': price_subtotal > 0.0 and price_subtotal or 0.0,
                'credit': price_subtotal < 0.0 and -price_subtotal or 0.0,
            }