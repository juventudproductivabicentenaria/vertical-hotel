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

    date_start = fields.Date(
        "Fecha de inicio",
        required=True,
        default=fields.Date.context_today,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )

    date_end = fields.Date(
        "Fecha de cierre",
        required=True,
        default=fields.Date.context_today,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )

    hotel_reservation = fields.Many2one(
        "hotel.reservation",
        "Reservacion",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )
    state = fields.Selection(
        [
            ("breakfast", "Desayuno"),
            ("lunch", "Almuerzo"),
            ("dinner", "Cena"),
            ("snack", "Merienda"),
        ],
        "Estado",
        default="draft",
    )
    type = fields.Selection(
        [
            ("draft", "Borrador"),
            ("confirm", "Confirmar"),
            ("cancel", "Cancelado"),
            ("done", "Hecho"),
        ],
        "Estado",
        default="draft",
    )

    partner_id = fields.Many2one(
        "res.partner",
        "Comensal",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]}
    )