from odoo import fields, models, api, _
import logging

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)


class ReserveRoom(models.TransientModel):
    _name = 'reserve.room'
    _description = 'Reserve room'

    date_from = fields.Datetime(
        'Date From', default=lambda self: fields.Date.today()
    )
    date_to = fields.Datetime(
        "Date To",
        default=lambda self: fields.Date.today() + relativedelta(days=1),
    )
    adults = fields.Integer('Adultos')
    boys = fields.Integer('Niños')

    def reservation_room(self, date_from, date_until, adults, ninos, rooms):
        room_obj = self.env['hotel.room']
        room_ids = room_obj.search([])
        reservation_line_obj = self.env['hotel.room.reservation.line']
        date_range_list = []
        domain = []
        # fecha_datetime = datetime.strptime(fecha_str, "%d-%m-%Y").replace(hour=0, minute=0, second=0)
        if date_from and date_until:
            # date_until = datetime.strptime(date_until, '%Y-%m-%d')
            # date_until = datetime.strptime(date_until+' 23:59:59', '%Y-%m-%d')
            # date_until =    date_until.replace(hour=23, minute=59, second=59)
            # # date_until = datetime.strptime(date_until, '%Y-%m-%dT%H:%M:%S')
            # date_from = datetime.strptime(date_until+' 00:00:01', '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            # date_from = date_from.replace(hour=0, minute=0, second=0)
            if self._context.get("tz", False):
                timezone = pytz.timezone(self._context.get("tz", False))
            else:
                timezone = pytz.timezone("UTC")

            d_to_obj = (
                date_until
                    .replace(tzinfo=pytz.timezone("UTC"))
                    .astimezone(timezone)
            )

            date_range_list.append(d_to_obj.strftime(dt))
            for chk_date_to in date_range_list:
                ch_dt_to = chk_date_to[:10] + ' 23:59:59'
                time_to = datetime.strptime(ch_dt_to, dt)
                c_to = time_to.replace(tzinfo=timezone).astimezone(
                    pytz.timezone("UTC")
                )
                chk_date_to = c_to.strftime(dt)  # self.date_to
                for room in room_ids:
                    reserline_ids = room.room_reservation_line_ids.ids  # Linea de reserva

                    # Linea que verifica si ya esta reservacion
                    reservline_ids = reservation_line_obj.search([
                        ('id', 'in', reserline_ids),
                        ('check_in', '<=', chk_date_to),
                        ('check_out', '>=', date_from),
                        # ('room_id.status', '=', 'occupied'),
                        # ('room_id.capacity', '=', capacity)
                    ])
                    print(reservline_ids)

                    if reservline_ids:
                        id = reservline_ids.room_id.id
                        domain.append(id)
                        print('1')
                print(domain)

                room_reserv = room_obj.search([
                    ('id', 'not in', domain),
                    ('is_published', '=', True)
                ])

                room_ids = room_reserv
        return room_ids
