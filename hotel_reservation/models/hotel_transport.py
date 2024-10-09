from . import tools
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import logging

_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)

class HotelTransport(models.Model):
    _name = "hotel.transport"
    _description = "Hotel Transport"
    _rec_name = "code"
    _order = "code"

    code = fields.Char(
        string="Codigo",  
    )
    hotel_reservation = fields.Many2one(
        "hotel.reservation",
        "Reservacion",
        required=False,
    )
    
    move_from = fields.Char(required=True, string="Transporte Desde")
    move_to = fields.Char(required=True, string="Transporte Hacia")

    move_from_2 =fields.Char(required=True, string="Transporte Desde(2)")
    move_to_2 = fields.Char(required=True, string="Transporte Hacia(2)")

    partner_id = fields.Many2one(
        "res.partner",
        "Pasajero",
        required=True,
    )
    departure_time = fields.Datetime(
        string="Hora de Salida", 
        required=True,
        
    )
    contact_number = fields.Char(
        string="Número de Contacto", 
        required=True,
    )
    
    departure_hour = fields.Char(
        string='Hora de Salida', 
        compute='_compute_departure_hour'
    )

    departure_hour_2 = fields.Char(
        string='Hora de Salida (2)', 
        compute='_compute_departure_hour_2'
    )

    departure_time_2 = fields.Datetime(
            string="Hora de Salida (2)", 
            required=True,   
    )

    @api.model
    def create(self, vals):
        vals["code"] = (
            self.env["ir.sequence"].next_by_code("hotel.transport") or "New"
        )
        res = super(HotelTransport, self).create(vals)
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Al cambiar al partner, actualizar el número de contacto."""
        if self.partner_id:
            self.contact_number = self.partner_id.phone

    def _compute_departure_hour(self):
        for record in self:
            if record.departure_time:
                record.departure_hour = record.departure_time.strftime('%H:%M:%S')
            else:
                record.departure_hour = ''

    def _compute_departure_hour_2(self):
        for record in self:
            if record.departure_time_2:
                record.departure_hour_2 = record.departure_time_2.strftime('%H:%M:%S')
            else:
                record.departure_hour_2 = ''