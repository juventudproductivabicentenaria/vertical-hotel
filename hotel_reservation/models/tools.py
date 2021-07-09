# -*- coding: utf-8 -*-

import hashlib
from odoo import fields


def default_hash(id=0):
    print("hash ejecutandose")
    print("hash ejecutandose")
    now = fields.Datetime.now().strftime("%m/%d/%Y,%H:%M:%S") + str(id)
    h = hashlib.new("sha1", now.encode())
    print(h.hexdigest())
    return h.hexdigest()

# session_token =fields.Char(string="Session",default=tools.default_hash(),required=True,size=20)
# from odoo.addons.tax_customer.models import tools
