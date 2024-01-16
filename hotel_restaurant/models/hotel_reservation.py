# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelReservation(models.Model):
    _name = "hotel.reservation"
    _description = "Includes Hotel Restaurant Table"

    hotel_reservation_orders_ids = fields.One2many(
                    "hotel.restaurant.order",
                    "reservation_room_id",
                    "Lines de pedido"
                    )