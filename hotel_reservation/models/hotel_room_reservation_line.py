# See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from . import tools
from odoo.exceptions import ValidationError

class HotelRoomReservationLine(models.Model):

    _name = "hotel.room.reservation.line"
    _description = "Hotel Room Reservation"
    _rec_name = "room_id"

    room_id = fields.Many2one("hotel.room", string="Room id", required=False)
    check_in = fields.Date("Check In Date", required=True)
    check_out = fields.Date("Check Out Date", required=True)

    state = fields.Selection(
        [("assigned", "Assigned"), ("unassigned", "Unassigned")], "Room Status"
    )
    reservation_id = fields.Many2one("hotel.reservation", "Reservation", required=False)
    reservation_line_id = fields.Many2one("hotel_reservation.line", "Reservation", required=False)
    parnert_id = fields.Many2one("res.partner", "Partner", related='reservation_line_id.partner_id')
    status = fields.Selection(string="state", related="reservation_id.state")
