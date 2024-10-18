# See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from . import tools
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)


class HotelReservation(models.Model):
    _name = "hotel.reservation"
    _rec_name = "reservation_no"
    _description = "Reservation"
    _order = "reservation_no desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _compute_folio_id(self):
        for res in self:
            res.update({"no_of_folio": len(res.folios_ids.ids)})

    def _has_default(self):
        return tools.default_hash()

    reservation_no = fields.Char("Reservation No", readonly=True, copy=False)
    date_order = fields.Datetime(
        "Date Ordered",
        readonly=True,
        required=True,
        index=True,
        default=lambda self: fields.Datetime.now(),
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        "Hotel",
        readonly=True,
        required=True,
        default=1,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Guest Name",
        readonly=True,
        required=True,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    
    pricelist_id = fields.Many2one(
        "product.pricelist",
        "Scheme",
        required=False,
        readonly=True,
        default=lambda self: self.env.user.company_id.pricelist_id.id,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        help="Pricelist for current reservation.",
    )
    partner_invoice_id = fields.Many2one(
        "res.partner",
        "Invoice Address",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        help="Invoice address for current reservation.",
    )
    partner_order_id = fields.Many2one(
        "res.partner",
        "Ordering Contact",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        help="The name and address of the "
        "contact that requested the order "
        "or quotation.",
    )
    partner_shipping_id = fields.Many2one(
        "res.partner",
        "Delivery Address",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        help="Delivery address" "for current reservation. ",
    )
    checkin = fields.Date(
        "Fecha prevista de llegada",
        required=True,
        readonly=True,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    checkout = fields.Date(
        "Fecha prevista de salida",
        required=True,
        readonly=True,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    adults = fields.Integer(
        "Adults",
        readonly=True,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        help="Number of adults there in the guest list. ",
    )
    children = fields.Integer(
        "Children",
        readonly=True,
        track_visibility='always',
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
        help="Number of children there in guest list.",
    )
    reservation_line_ids = fields.One2many(
        "hotel_reservation.line",
        "line_id",
        "Reservation Line",
        help="Hotel room reservation details.",
        ondelete='cascade',
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("cancel", "Cancel"),
            ("done", "Done"),
        ],
        "State",
        readonly=True,
        default="draft",
    )
    
    folios_ids = fields.Many2many(
        "hotel.folio",
        "hotel_folio_reservation_rel",
        "order_id",
        "invoice_id",
        string="Folio",
    )
    
    # foods_ids = fields.One2many(
    #     "hotel.foods",
    #     "hotel_reservation",
    #     string="Food"
    # )

    activities_ids = fields.One2many(
        "hotel.housekeeping.activities",
        "reservation_id",
        string="Actividades"
    )
    
    transport_ids = fields.One2many(
        "hotel.transport",
        "hotel_reservation",
        string="Transport"
    )
    
    reservation_orders_lines_ids = fields.One2many(
        "hotel.restaurant.order.list",
        "reservation_room_id",
        "Lines de pedido"
    )

    no_of_folio = fields.Integer("No. Folio", compute="_compute_folio_id")
    token = fields.Char(string="token", default=lambda self: self._has_default(), required=True)


    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for reserv_rec in self:
            if reserv_rec.state != "draft":
                raise ValidationError(
                    _(
                        "Sorry, you can only delete the reservation when it's draft!"
                    )
                )
        return super(HotelReservation, self).unlink()

    def copy(self):
        ctx = dict(self._context) or {}
        ctx.update({"duplicate": True})
        return super(HotelReservation, self.with_context(ctx)).copy()

    @api.constrains("reservation_line_ids", "adults", "children")
    def check_reservation_rooms(self):
        """
        This method is used to validate the reservation_line_ids.
        -----------------------------------------------------
        @param self: object pointer
        @return: raise a warning depending on the validation
        """
        ctx = dict(self._context) or {}
        for reservation in self:
            cap = 0
            # for rec in reservation.reservation_line_ids:
            #     if not rec.reserve:
            #         raise ValidationError(
            #             _("Please Select Rooms For Reservation.")
            #         )
            #     cap = sum(room.capacity for room in rec.reserve)
            # if not ctx.get("duplicate"):
            #     if (reservation.adults + reservation.children) > cap:
            #         raise ValidationError(
            #             _(
            #                 "Room Capacity Exceeded \n"
            #                 " Please Select Rooms According to"
            #                 " Members Accomodation."
            #             )
            #         )
            # if reservation.adults <= 0:
            #     raise ValidationError(
            #         _("Number of Adults must be Positive value.")
            #     )

    # @api.constrains("checkin", "checkout")
    # def check_in_out_dates(self):
    #     """
    #     When date_order is less then check-in date or
    #     Checkout date should be greater than the check-in date.
    #     """
    #     if self.checkout and self.checkin:
    #         if self.checkin < self.date_order:
    #             raise ValidationError(
    #                 _(
    #                     """Check-in date should be greater than """
    #                     """the current date."""
    #                 )
    #             )
    #         if self.checkout < self.checkin:
    #             raise ValidationError(
    #                 _(
    #                     """Check-out date should be greater """
    #                     """than Check-in date."""
    #                 )
    #             )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        """
        if not self.partner_id:
            self.update(
                {
                    "partner_invoice_id": False,
                    "partner_shipping_id": False,
                    "partner_order_id": False,
                }
            )
        else:
            addr = self.partner_id.address_get(
                ["delivery", "invoice", "contact"]
            )
            self.update(
                {
                    "partner_invoice_id": addr["invoice"],
                    "partner_shipping_id": addr["delivery"],
                    "partner_order_id": addr["contact"],
                    "pricelist_id": self.partner_id.property_product_pricelist.id,
                }
            )

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        vals["reservation_no"] = (
            self.env["ir.sequence"].next_by_code("hotel.reservation") or "New"
        )
        reservation = super(HotelReservation,self).create(vals)
        return reservation 

    def check_overlap(self, date1, date2):
        delta = date2 - date1
        return {date1 + timedelta(days=i) for i in range(delta.days + 1)}

    
    def confirm_reservation(self):
        """
        This method creates a new record set for hotel room reservation line
        -------------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel room reservation line.
        """
        reservation_line_obj = self.env["hotel.room.reservation.line"].sudo()
        vals = {}
        
        for reservation in self:
            reserv_checkin = reservation.checkin
            reserv_checkout = reservation.checkout
            room_bool = False
            
            if not reservation.reservation_line_ids:  # Si no hay líneas de reserva
                self.state = "confirm"
                vals = {
                    "check_in": reservation.checkin,
                    "check_out": reservation.checkout,
                    "state": "assigned",
                    "reservation_id": reservation.id,
                }
                reservation_line_obj.create(vals)
            else:
                for line_id in reservation.reservation_line_ids:
                    room = line_id.hotel_room_id
                    if room and room.room_reservation_line_ids:
                        for reserv in room.room_reservation_line_ids.search(
                                [
                                    ("status", "in", ("confirm", "done")),
                                    ("room_id", "=", room.id),
                                ]
                            ):
                                check_in = reserv.check_in
                                check_out = reserv.check_out
                                if check_in <= reserv_checkin <= check_out:
                                    room_bool = True
                                if check_in <= reserv_checkout <= check_out:
                                    room_bool = True
                                if (
                                    reserv_checkin <= check_in
                                    and reserv_checkout >= check_out
                                ):
                                    room_bool = True
                                r_checkin = (reservation.checkin)
                                r_checkout = (reservation.checkout)
                                check_intm = (reserv.check_in)
                                check_outtm = (reserv.check_out)
                                range1 = [r_checkin, r_checkout]
                                range2 = [check_intm, check_outtm]
                                overlap_dates = self.check_overlap(
                                    *range1
                                ) & self.check_overlap(*range2)
                                if room_bool:
                                    raise ValidationError(
                                        _(
                                            "You tried to Confirm "
                                            "Reservation with room"
                                            " those already "
                                            "reserved in this "
                                            "Reservation Period. "
                                            "Overlap Dates are "
                                            "%s"
                                        )
                                        % overlap_dates
                                    )
                                else:
                                    self.state = "confirm"
                                    vals = {
                                        "room_id": room.id,
                                        "check_in": reservation.checkin,
                                        "check_out": reservation.checkout,
                                        "state": "assigned",
                                        "reservation_id": reservation.id,
                                    }
                                    room.write(
                                        {"isroom": False, "status": "occupied"}
                                    )
                    else:
                        self.state = "confirm"
                        vals = {
                            "check_in": reservation.checkin,
                            "check_out": reservation.checkout,
                            "state": "assigned",
                            "reservation_id": reservation.id,
                        }
                        reservation_line_obj.create(vals)

            template_id = self.env.ref('hotel_reservation.email_templates_hotel_reservation') 
            if template_id:
                template_id.send_mail(reservation.id, force_send=True)
    
        return True


    def cancel_reservation(self):
        """
        This method cancel record set for hotel room reservation line
        ------------------------------------------------------------------
        @param self: The object pointer
        @return: cancel record set for hotel room reservation line.
        """
        room_res_line_obj = self.env["hotel.room.reservation.line"].sudo()
        hotel_res_line_obj = self.env["hotel_reservation.line"]
        self.state = "cancel"
        room_reservation_line = room_res_line_obj.search(
            [("reservation_id", "in", self.ids)]
        )
        room_reservation_line.write({"state": "unassigned"})
        room_reservation_line.unlink()
        reservation_lines = hotel_res_line_obj.search(
            [("line_id", "in", self.ids)]
        )
        for reservation_line in reservation_lines:
            reservation_line.hotel_room_id.write(
                {"isroom": True, "status": "available"}
            )

            template_id = self.env.ref("hotel_reservation.email_templates_hotel_reservation_cancellation")  
            if template_id:
                template_id.send_mail(self.id, force_send=True)
        
        return True 


    def set_to_draft_reservation(self):
        self.update({"state": "draft"})

    def action_send_reservation_mail(self):
        """
        This function opens a window to compose an email,
        template message loaded by default.
        @param self: object pointer
        """
        self.ensure_one() 
        template_id = self.env.ref(
            "hotel_reservation.email_templates_hotel_reservation_request", raise_if_not_found=False
        )

        if template_id:
            template_id.send_mail(self.id, force_send=True)
        else:
            raise ValueError("No se pudo encontrar la plantilla de correo 'hotel_reservation.email_templates_hotel_reservation_request'.")
        return True

    def get_guest_first_line(self): 
        return  self.reservation_line_ids[0]
    
    def get_has_food(self):
        return 'Si' if len(self.reservation_orders_lines_ids) > 0 else 'No'

    @api.model
    def _reservation_reminder_24hrs(self):
        """
        This method is for scheduler
        every 1day scheduler will call this method to
        find all tomorrow's reservations.
        ----------------------------------------------
        @param self: The object pointer
        @return: send a mail
        """
        now_date = fields.Date.today()
        template_id = self.env.ref(
            "hotel_reservation.mail_template_reservation_reminder_24hrs"
        )
        for reserv_rec in self:
            checkin_date = reserv_rec.checkin
            difference = relativedelta(now_date, checkin_date)
            if (
                difference.days == -1
                and reserv_rec.partner_id.email
                and reserv_rec.state == "confirm"
            ):
                template_id.send_mail(reserv_rec.id, force_send=True)
        return True

    def create_folio(self):
        """
        This method is for create new hotel folio.
        -----------------------------------------
        @param self: The object pointer
        @return: new record set for hotel folio.
        """
        hotel_folio_obj = self.env["hotel.folio"]
        for reservation in self:
            folio_lines = []
            checkin_date = reservation["checkin"]
            checkout_date = reservation["checkout"]
            duration_vals = self._onchange_check_dates(
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                duration=False,
            )
            duration = duration_vals.get("duration") or 0.0
            folio_vals = {
                "date_order": reservation.date_order,
                "warehouse_id": reservation.warehouse_id.id,
                "partner_id": reservation.partner_id.id,
                "pricelist_id": reservation.pricelist_id.id,
                "partner_invoice_id": reservation.partner_invoice_id.id,
                "partner_shipping_id": reservation.partner_shipping_id.id,
                "checkin_date": reservation.checkin,
                "checkout_date": reservation.checkout,
                "duration": duration,
                "reservation_id": reservation.id,
            }
            for line in reservation.reservation_line_ids:
                roon = line.hotel_room_id
                if roon:
                    folio_lines.append(
                        (
                            0,
                            0,
                            {
                                "checkin_date": checkin_date,
                                "checkout_date": checkout_date,
                                "product_id": roon.product_id and roon.product_id.id,
                                "name": reservation["reservation_no"],
                                "price_unit": roon.list_price,
                                "product_uom_qty": duration,
                                "is_reserved": True,
                            },
                        )
                    )
                    roon.write({"status": "occupied", "isroom": False})
            folio_vals.update({"room_line_ids": folio_lines})
            folio = hotel_folio_obj.create(folio_vals)
            for rm_line in folio.room_line_ids:
                rm_line.product_id_change()
            self.write({"folios_ids": [(6, 0, folio.ids)], "state": "done"})
        return True

    def _onchange_check_dates(
        self, checkin_date=False, checkout_date=False, duration=False
    ):
        """
        This method gives the duration between check in checkout if
        customer will leave only for some hour it would be considers
        as a whole day. If customer will checkin checkout for more or equal
        hours, which configured in company as additional hours than it would
        be consider as full days
        --------------------------------------------------------------------
        @param self: object pointer
        @return: Duration and checkout_date
        """
        value = {}
        configured_addition_hours = (
            self.warehouse_id.company_id.additional_hours
        )
        duration = 0
        if checkin_date and checkout_date:
            dur = checkout_date - checkin_date
            duration = dur.days + 1
            if configured_addition_hours > 0:
                additional_hours = abs(dur.seconds / 60)
                if additional_hours <= abs(configured_addition_hours * 60):
                    duration -= 1
        value.update({"duration": duration})
        return value

    def open_folio_view(self):
        folios = self.mapped("folios_ids")
        action = self.env.ref("hotel.open_hotel_folio1_form_tree_all").read()[
            0
        ]
        if len(folios) > 1:
            action["domain"] = [("id", "in", folios.ids)]
        elif len(folios) == 1:
            action["views"] = [
                (self.env.ref("hotel.view_hotel_folio_form").id, "form")
            ]
            action["res_id"] = folios.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
