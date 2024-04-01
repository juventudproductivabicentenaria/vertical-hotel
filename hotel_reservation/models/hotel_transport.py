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

class HotelTransport(models.Model):
    _name = "hotel.transport"
    _description = "Hotel Transport"

    hotel_reservation = fields.Many2one(
        "hotel.reservation",
        "Reservacion",
        required=False,
    )
    
    move_from = fields.Char(required=True, string="Transporte Desde")
    
    move_to = fields.Char(required=True, string="Transporte Hacia")

    partner_id = fields.Many2one(
        "res.partner",
        "Pasajero",
        required=True,
    )