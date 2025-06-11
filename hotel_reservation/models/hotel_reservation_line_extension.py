from odoo import models, fields

class HotelReservationLine(models.Model):
    _inherit = "hotel_reservation.line"

    restaurant_order_ids = fields.One2many(
        "hotel.restaurant.order.list",
        "reservation_line",
        string="Órdenes de restaurante"
    )

class HotelRestaurantOrderList(models.Model):
    _inherit = "hotel.restaurant.order.list"

    reservation_line = fields.Many2one("hotel_reservation.line", string="Línea de reserva")
