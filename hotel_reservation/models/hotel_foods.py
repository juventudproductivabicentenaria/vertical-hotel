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

    name = fields.Char(
        string="Nombre",
        required=True,
        
        readonly=True,
        states={"draft": [("readonly", False)]}
    )
    data = fields.Binary("Image", required=True, attachment=True)

    date_start = fields.Date(
        string="Fecha de inicio",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )
    date_end = fields.Date(
        string="Fecha de finalización",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )
    
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("published", "Publicado"),
            ("cancel", "Cancelado"),
        ],
        "Estado",
        default="draft",
    )

    def action_set_to_draft(self):
        self.write({"state": "draft"})
    
    def action_set_cancel(self):
        self.write({"state": "cancel"})

    def action_set_to_publish(self):
        self.write({"state": "published"})

    @api.model
    def create(self, vals):
        # vals["code"] = (
        #     self.env["ir.sequence"].next_by_code("hotel.foods") or "New"
        # )
        res = super(HotelFoods, self).create(vals)
        return res

    def get_MenuHotelFoods(self, date_start, date_end):
        # food_image = request.env['hotel.foods'].sudo().search([
        #     ('state', '=', 'published'),
        #     ('date_start', '<=', date_start),
        #     ('date_end', '>=', date_end),
        # ],limit=1
        query = """ SELECT atl.id
                FROM hotel_foods as atl
                WHERE atl.state = 'published'  AND 
                ((atl.date_start >= %s AND atl.date_end <= %s) OR 
                (atl.date_start < %s AND atl.date_end <= %s AND atl.date_end >= %s) OR 
                (atl.date_start >= %s AND atl.date_start <= %s AND atl.date_end > %s) OR
                (atl.date_start < %s AND  atl.date_end > %s) 
               );
            """ 
        params = [
            date_start, date_end, 
            date_start, date_end, date_start,
            date_start, date_end, date_end,
            date_start, date_end,
        ]
        self._cr.execute(query, params)
        food_image = self._cr.dictfetchone()
        return food_image