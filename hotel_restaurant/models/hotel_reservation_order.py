# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelReservationOrder(models.Model):

    _name = "hotel.reservation.order"
    _description = "Reservation Order"
    _rec_name = "order_number"
    _order = 'order_number desc'

    order_number = fields.Char("Order No", readonly=True)
    
    reservation_id = fields.Many2one(
        "hotel.restaurant.reservation", "Reservation No"
    )
    reservation_room_id = fields.Many2one(
        "hotel.reservation", "Reservacion"
    )
    order_date = fields.Datetime(
        "Date", required=True, default=lambda self: fields.Datetime.now()
    )
    partner_id = fields.Many2one("res.partner", "Solicitante")

    waitername = fields.Many2one("res.partner", "Waiter Name")

    table_nos_ids = fields.Many2many(
        "hotel.restaurant.tables",
        "temp_table4",
        "table_no",
        "name",
        "Table Number",
    )

    order_list_ids = fields.One2many(
        "hotel.restaurant.order.list", "reservation_order_id", "Order List"
    )

    tax = fields.Float("Tax (%) ")
    amount_subtotal = fields.Float(
        compute="_compute_amount_all_total", string="Subtotal"
    )
    amount_total = fields.Float(
        compute="_compute_amount_all_total", string="Total"
    )
    kitchen = fields.Integer("Kitchen Id")
    rests_ids = fields.Many2many(
        "hotel.restaurant.order.list",
        "reserv_id",
        "kitchen_id",
        "res_kit_ids",
        "Rest",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("order", "Order Created"), ("done", "Done")],
        "State",
        required=True,
        readonly=True,
        default="draft",
    )
    folio_id = fields.Many2one("hotel.folio", "Folio No", domain="[('reservation_id','=',reservation_room_id)]")
    is_folio = fields.Boolean(
        "Is a Hotel Guest??", help="is customer reside in hotel or not"
    )


    @api.depends("order_list_ids")
    def _compute_amount_all_total(self):
        """
        amount_subtotal and amount_total will display on change of order_list_ids
        ---------------------------------------------------------------------
        @param self: object pointer
        """
        for sale in self:
            sale.amount_subtotal = sum(
                line.price_subtotal for line in sale.order_list_ids
            )
            sale.amount_total = (
                sale.amount_subtotal + (sale.amount_subtotal * sale.tax) / 100
            )

    def reservation_generate_kot(self):
        """
        This method create new record for hotel restaurant order list.
        --------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel restaurant order list.
        """
        res = []
        order_tickets_obj = self.env["hotel.restaurant.kitchen.order.tickets"]
        rest_order_list_obj = self.env["hotel.restaurant.order.list"]
        for order in self:
            if not order.order_list_ids:
                raise ValidationError(_("Please Give an Order"))
            table_ids = order.table_nos_ids.ids
            line_data = {
                "orderno": order.order_number,
                "resno": order.reservation_id.reservation_id,
                "kot_date": order.order_date,
                "w_name": order.waitername.name,
                "table_nos_ids": [(6, 0, table_ids)],
            }
            kot_data = order_tickets_obj.create(line_data)
            for order_line in order.order_list_ids:
                o_line = {
                    "kot_order_id": kot_data.id,
                    "menucard_id": order_line.menucard_id.id,
                    "item_qty": order_line.item_qty,
                    "item_rate": order_line.item_rate,
                }
                rest_order_list_obj.create(o_line)
                res.append(order_line.id)
            order.update(
                {
                    "kitchen": kot_data.id,
                    "rests_ids": [(6, 0, res)],
                    "state": "order",
                }
            )
        return res

    def reservation_update_kot(self):
        """
        This method update record for hotel restaurant order list.
        ----------------------------------------------------------
        @param self: The object pointer
        @return: update record set for hotel restaurant order list.
        """
        order_tickets_obj = self.env["hotel.restaurant.kitchen.order.tickets"]
        rest_order_list_obj = self.env["hotel.restaurant.order.list"]
        for order in self:
            table_ids = order.table_nos_ids.ids
            line_data = {
                "orderno": order.order_number,
                "resno": order.reservation_id.reservation_id,
                "kot_date": fields.Datetime.to_string(fields.datetime.now()),
                "w_name": order.waitername.name,
                "table_nos_ids": [(6, 0, table_ids)],
            }
            kot_id = order_tickets_obj.browse(self.kitchen)
            kot_id.write(line_data)
            for order_line in order.order_list_ids:
                if order_line not in order.rests_ids.ids:
                    kot_data = order_tickets_obj.create(line_data)
                    o_line = {
                        "kot_order_id": kot_data.id,
                        "menucard_id": order_line.menucard_id.id,
                        "item_qty": order_line.item_qty,
                        "item_rate": order_line.item_rate,
                    }
                    order.update(
                        {
                            "kitchen": kot_data.id,
                            "rests_ids": [(4, order_line.id)],
                        }
                    )
                    rest_order_list_obj.create(o_line)
        return True

    def done_kot(self):
        """
        This method is used to change the state
        to done of the hotel reservation order
        ----------------------------------------
        @param self: object pointer
        """
        hsl_obj = self.env["hotel.service.line"]
        so_line_obj = self.env["sale.order.line"]
        for res_order in self:
            for order in res_order.order_list_ids:
                if res_order.folio_id:
                    values = {
                        "order_id": res_order.folio_id.order_id.id,
                        "name": order.menucard_id.name,
                        "product_id": order.menucard_id.product_id.id,
                        "product_uom_qty": order.item_qty,
                        "price_unit": order.item_rate,
                        "price_subtotal": order.price_subtotal,
                    }
                    sol_rec = so_line_obj.create(values)
                    hsl_obj.create(
                        {
                            "folio_id": res_order.folio_id.id,
                            "service_line_id": sol_rec.id,
                        }
                    )
                    res_order.folio_id.write(
                        {"hotel_reservation_orders_ids": [(4, res_order.id)]}
                    )
            res_order.reservation_id.write({"state": "done"})
        self.write({"state": "done"})
        return True
        
    @api.onchange('reservation_room_id')
    def _onchange_reservation_room_id(self):
        self.folio_id = False
        pass


    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        seq_obj = self.env["ir.sequence"]
        print()
        res_oder = seq_obj.next_by_code("hotel.reservation.order") or "New"
        vals["order_number"] = res_oder
        return super(HotelReservationOrder, self).create(vals)


class HotelRestaurantOrderList(models.Model):
    _name = "hotel.restaurant.order.list"
    _description = "Includes Hotel Restaurant Order"

    @api.depends("item_qty", "item_rate")
    def _compute_price_subtotal(self):
        """
        price_subtotal will display on change of item_rate
        --------------------------------------------------
        @param self: object pointer
        """
        for line in self:
            line.price_subtotal = line.item_rate * int(line.item_qty)

    @api.onchange("menucard_id")
    def _onchange_item_name(self):
        """
        item rate will display on change of item name
        ---------------------------------------------
        @param self: object pointer
        """
        self.item_rate = self.menucard_id.list_price

    restaurant_order_id = fields.Many2one(
        "hotel.restaurant.order", "Restaurant Order"
    )
    
    reservation_line = fields.Many2one("hotel_reservation.line", "linea de reserva")

    partner_id = fields.Many2one(
        "res.partner",
        "Comensal",
        required=True
    ) 
    reservation_order_id = fields.Many2one(
        "hotel.reservation.order", "Reservation Order"
    )
    
    reservation_room_id = fields.Many2one(
        "hotel.reservation", "Reservacion",
    )
    kot_order_id = fields.Many2one(
        "hotel.restaurant.kitchen.order.tickets", "Kitchen Order Tickets"
    )
    date_order = fields.Date(
        "Fecha de orden", required=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("order", "Order Created"), ("done", "Done")],
        "State",
        related='reservation_order_id.state', store=True
)
    type_solicitation = fields.Selection([
            ("breakfast", "Desayuno"),
            ("lunch", "Almuerzo"),
            ("dinner", "Cena"),
            ("snack", "Merienda"),
        ],"Tipo de Solicitud"
    )
    
    menucard_id = fields.Many2one("hotel.menucard", "Item Name",  
        required=False)

    item_qty = fields.Integer("Qty", required=True, default=1)
    item_rate = fields.Float("Rate")

    price_subtotal = fields.Float(
        compute="_compute_price_subtotal", string="Subtotal"
    )
    # @api.onchange('reservation_order_id')
    # def onchange_reservation_order_id(self):
    #     if self.reservation_order_id and self.reservation_order_id.reservation_room_id:
    #         self.reservation_room_id = self.reservation_order_id.reservation_room_id
    