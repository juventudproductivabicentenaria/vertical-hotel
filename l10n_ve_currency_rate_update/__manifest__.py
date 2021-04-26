# -*- coding: utf-8 -*-
{
    'name': "Currency Rate Update",
    'version': '0.1',
    'author': "Soluciones SoftHard",
    "license": "AGPL-3",
    "website": "http://www.solucionesofthard.com/",
    'category': 'Generic Modules/Accounting',
    'depends': ['base',
                'account',
                'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/res_currency_rate_provider.xml',
        'wizard/res_currency_rate_update_wizard.xml',
        'data/res_currency_rate_provider.xml',
        'data/cron.xml',
        'data/email_template_data.xml',
    ],
}
