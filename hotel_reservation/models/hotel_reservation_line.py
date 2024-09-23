# See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from . import tools
from odoo.exceptions import ValidationError

class HotelReservationLine(models.Model):

    _name = "hotel_reservation.line"
    _description = "Reservation Line"
    _rec_name = "code"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    name = fields.Text("Descripcion")
    hotel_room_id = fields.Many2one("hotel.room", "Habitacion", default= "", required=False, track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},)

    line_id = fields.Many2one("hotel.reservation","Reservacion", readonly=True,track_visibility='always',)

    code = fields.Char("Codigo", readonly=True)

    is_son = fields.Boolean("Ninos")
    is_couple = fields.Boolean("Pareja")
    
    include_room = fields.Boolean("Incluir Habitación")
    institution_from = fields.Char(string="Institución de donde nos visitan", readonly=False, required=False, default=None)
    couple_id = fields.Many2one(
        "res.partner",
        "Pareja",
        track_visibility='always', )
    
    children_ids = fields.Many2many(
        "res.partner",
        string="Hijos (a)")

    partner_id = fields.Many2one(
        "res.partner",
        "Huesped",
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("cancel", "Cancel"),
            ("done", "Done"),
        ],
        "Estado",
        readonly=True,
        related='line_id.state', store=True
    )

    checkin = fields.Datetime(
        "Fecha prevista de llegada",
        required=True,
        related='line_id.checkin',
        store=True,
        # readonly=True,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    checkout = fields.Datetime(
        "Fecha prevista de salida",
        required=True,
        # readonly=True,
        related='line_id.checkout',
        store=True,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    room_reservation_line =  fields.Many2one("hotel.room.reservation.line", "linea de reserva", required=False)
    
    def write(self, vals):
        res = super(HotelReservationLine, self).write(vals)
        if vals.get("hotel_room_id"):
            HotelRoomReservation =  self.env["hotel.room.reservation.line"].sudo()
            reservation_line_ids = HotelRoomReservation.search([
                ('reservation_id', '=', self.line_id.id),
                ('state', '=', 'assigned'),
                ('reservation_line_id', '=', self.id),
            ])
            if reservation_line_ids:
                reservation_line_ids.unlink()

            roon_reservation_id = HotelRoomReservation.create({
                "room_id": vals.get("hotel_room_id"),
                "check_in": self.line_id.checkin,
                "check_out": self.line_id.checkout,
                "state": "assigned",
                "reservation_id": self.line_id.id,
                "reservation_line_id": self.id,
            })
            
            # vals["room_reservation_line"] = roon_reservation_id.id
            
        if self.hotel_room_id and self.hotel_room_id.clean_type_ids:
            HotelHousekeeping = self.env["hotel.housekeeping"].sudo()
            housekeeping_ids = HotelHousekeeping.search([
                        ('room_id', '=', self.hotel_room_id.id), 
                        ('reservation_id', '=', self.line_id.id),
                    ])
            if housekeeping_ids:
                housekeeping_ids.activity_line_ids.unlink()
                housekeeping_ids.unlink()


            for line in self.hotel_room_id.clean_type_ids:
                housekeeping_id = HotelHousekeeping.create({
                    "current_date": self.line_id.date_order if self.line_id else fields.Date.today(),
                    "room_id": self.hotel_room_id.id,
                    "clean_type": line.id,
                    "inspector_id": self.env.user.id,
                    "reservation_id": self.line_id.id,
                })
                if line.clean_activity_line_ids:
                    for activity in line.clean_activity_line_ids:
                        housekeeping_id.activity_line_ids.create({
                            "activity_id": activity.activity_id.id,
                            "housekeeping_id": housekeeping_id.id,
                            "reservation_id": self.line_id.id,
                            })
        return res

        
    
    @api.model
    def create(self, vals):
        vals["code"] = (
            self.env["ir.sequence"].next_by_code("hotel.reservation.line") or "New"
        )
        res = super(HotelReservationLine, self).create(vals)
        if res.hotel_room_id:
            HotelRoomReservation =  self.env["hotel.room.reservation.line"].sudo()
            reservation_line_ids = HotelRoomReservation.search([
                ('reservation_id', '=', res.line_id.id),
                ('state', '=', 'assigned'),
                ('reservation_line_id', '=', res.id),
            ])
            if reservation_line_ids:
                reservation_line_ids.unlink()

            roon_reservation_id = HotelRoomReservation.create({
                "room_id": res.hotel_room_id.id,
                "check_in": res.line_id.checkin,
                "check_out": res.line_id.checkout,
                "state": "assigned",
                "reservation_id": res.line_id.id,
                "reservation_line_id": res.id,
            })
            res.room_reservation_line = roon_reservation_id.id
            
        if res.hotel_room_id and res.hotel_room_id.clean_type_ids:
            HotelHousekeeping = self.env["hotel.housekeeping"].sudo()
            housekeeping_ids = HotelHousekeeping.search([
                        ('room_id', '=', res.hotel_room_id.id), 
                        ('reservation_id', '=', res.line_id.id),
                    ])
            if housekeeping_ids:
                housekeeping_ids.activity_line_ids.unlink()
                housekeeping_ids.unlink()


            for line in res.hotel_room_id.clean_type_ids:
                housekeeping_id = HotelHousekeeping.create({
                    "current_date": res.line_id.date_order if res.line_id else fields.Date.today(),
                    "room_id": res.hotel_room_id.id,
                    "clean_type": line.id,
                    "inspector_id": self.env.user.id,
                    "reservation_id": res.line_id.id,
                })
                if line.clean_activity_line_ids:
                    for activity in line.clean_activity_line_ids:
                        housekeeping_id.activity_line_ids.create({
                            "activity_id": activity.activity_id.id,
                            "housekeeping_id": housekeeping_id.id,
                            "reservation_id": res.line_id.id,
                            })
        return res
    
    @api.onchange("categ_id")
    def _onchange_categ(self):
        """
        When you change categ_id it check checkin and checkout are
        filled or not if not then raise warning
        -----------------------------------------------------------
        @param self: object pointer
        """
        if not self.line_id.checkin:
            raise ValidationError(
                _(
                    """Before choosing a room,\n You have to """
                    """select a Check in date or a Check out """
                    """ date in the reservation form."""
                )
            )
        elif not self.line_id.checkout:
            raise ValidationError(
                _(
                    """Before choosing a room, \n You have to """
                    """select a departure date """
                    """date on the reservation form."""
                )
            )
        hotel_room_ids = self.env["hotel.room"].search(
            [("room_categ_id", "=", self.categ_id.id)]
        )
        room_ids = []
        for room in hotel_room_ids:
            assigned = False
            for line in room.room_reservation_line_ids:
                if line.status != "cancel":
                    if (
                        self.line_id.checkin
                        <= line.check_in
                        <= self.line_id.checkout
                    ) or (
                        self.line_id.checkin
                        <= line.check_out
                        <= self.line_id.checkout
                    ):
                        assigned = True
                    elif (
                        line.check_in <= self.line_id.checkin <= line.check_out
                    ) or (
                        line.check_in
                        <= self.line_id.checkout
                        <= line.check_out
                    ):
                        assigned = True
            for rm_line in room.room_line_ids:
                if rm_line.status != "cancel":
                    if (
                        self.line_id.checkin
                        <= rm_line.check_in
                        <= self.line_id.checkout
                    ) or (
                        self.line_id.checkin
                        <= rm_line.check_out
                        <= self.line_id.checkout
                    ):
                        assigned = True
                    elif (
                        rm_line.check_in
                        <= self.line_id.checkin
                        <= rm_line.check_out
                    ) or (
                        rm_line.check_in
                        <= self.line_id.checkout
                        <= rm_line.check_out
                    ):
                        assigned = True
            if not assigned:
                room_ids.append(room.id)
        domain = {"reserve": [("id", "in", room_ids)]}
        return {"domain": domain}

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        hotel_room_reserv_line_obj = self.env["hotel.room.reservation.line"].sudo()
        for reserv_rec in self:
            if not reserv_rec.state == 'draft':
                raise ValidationError(
                        _(
                            "Sorry, you can only delete the reservation when it's draft!"
                        )
                    )
            rec = reserv_rec.hotel_room_id
            if rec:
                lines = hotel_room_reserv_line_obj.search(
                    [
                        ("room_id", "=", rec.id),
                        ("reservation_id", "=", reserv_rec.line_id.id),
                    ]
                )
                if lines:
                    rec.write({"isroom": True, "status": "available"})
                    lines.unlink()
        return super(HotelReservationLine, self).unlink()


