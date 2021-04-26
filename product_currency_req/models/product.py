# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime

class AccountMove(models.Model):
    _inherit = "product.template"

    amount_currency_ext = fields.Float('Importe', compute='_get_amount_currency_ext')
    currency_ext = fields.Many2one('res.currency', 'Modena')
    currency_company = fields.Many2one('res.currency', compute='_get_currency_company')
    select_currency = fields.Selection([
        ('orig', 'Moneda de Compañía'),
        ('fora', 'Moneda Foranea')],
        string='Selector de Moneda', default='orig')

    def _get_currency_company(self):
        self.currency_company = self.env.company.currency_id.id

    def _get_amount_currency_ext(self):
        self.amount_currency_ext = float(self.currency_ext._convert(self.list_price, self.env.company.currency_id, self.env.company, datetime.datetime.now()))

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            if template.currency_ext and template.select_currency == 'fora':
                template.currency_id = template.currency_ext.id
            else:
                template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id




    @api.depends_context('force_company')
    def _compute_cost_currency_id(self):
        # Cost_currency_id is the displayed currency for standard_price
        # which is company_dependent and thus depends on force_company
        # context key (or self.env.company)
        company_id = self._context.get('force_company') or self.env.company.id
        company = self.env['res.company'].browse(company_id)
        for template in self:
            if template.currency_ext and template.select_currency == 'fora':
                template.cost_currency_id = template.currency_ext.id
            else:
                template.cost_currency_id = company.currency_id.id