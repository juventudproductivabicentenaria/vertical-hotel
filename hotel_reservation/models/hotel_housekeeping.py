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

class HotelHousekeepingActivities(models.Model):
    _inherit = "hotel.housekeeping"

    reservation_id = fields.Many2one("hotel.reservationn", "Reservation", readonly=True)

    is_rreservation = fields.Boolean(
        "Reservation",
        default=False,
        )
    reservation_line_id = fields.Many2one( "hotel.reservation.line", "Reservation Line", required=False) 

class HotelHousekeepingActivities(models.Model):
    _inherit = "hotel.housekeeping.activities"

    reservation_id = fields.Many2one("hotel.reservation", "Reservation")
