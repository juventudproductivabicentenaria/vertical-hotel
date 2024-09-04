# See LICENSE file for full copyright and licensing details.
import logging
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from . import tools

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt

_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)

class HotelFoods(models.Model):
    _name = "hotel.foods"
    _description = "Hotel Foods"
    _rec_name = "name"
    _order = "date_start"

    # code = fields.Char(
    #     string="Codigo",  
    # )
    name = fields.Char(
        string="Nombre",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )

    date_start = fields.Date(
        string="Fecha",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )
    date_end = fields.Date(
        string="Fecha",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )
    
    state = fields.Selection(
        [
            ("published", "Publicado"),
            ("draft", "Borrador"),
            ("candela", "Cancelado"),
        ],
        "Estado",
        default="draft",
    )


    @api.model
    def create(self, vals):
        # vals["code"] = (
        #     self.env["ir.sequence"].next_by_code("hotel.foods") or "New"
        # )
        res = super(HotelFoods, self).create(vals)
        return res