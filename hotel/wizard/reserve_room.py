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

    def reservation_room(self):
        room_obj = self.env['hotel.room']
        room_ids = room_obj.search([])
        reservation_line_obj = self.env['hotel.room.reservation.line']
        date_range_list = []
        today = datetime.today()
        capacity = self.adults + self.boys

        print('capacyti')
        print(capacity)
        print(capacity)

        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise UserError(
                    _('The departure date must be greater than the arrival date.')
                )
            if self.date_from < today:
                raise UserError(
                    _('La fecha de inicio debe ser mayor o igual a la del dia de hoy')
                )
            if self._context.get("tz", False):
                timezone = pytz.timezone(self._context.get("tz", False))
            else:
                timezone = pytz.timezone("UTC")
            d_frm_obj = (
                self.date_from
                .replace(tzinfo=pytz.timezone("UTC"))
                .astimezone(timezone) - relativedelta(days=1)
            )
            d_to_obj = (
                self.date_to
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
                    date_from = self.date_from - relativedelta(days=1)
                    date_to = self.date_to
                    print('date_from')
                    print(date_from)
                    print(chk_date_to)
                    reserline_ids = room.room_reservation_line_ids.ids  # Linea de reserva

                    # Linea que verifica si ya esta reservacion
                    reservline_ids = reservation_line_obj.search([
                        ('id', 'in', reserline_ids),
                        ('check_in', '<=', chk_date_to),
                        ('check_out', '>=', date_from),
                        ('room_id.status', '=', 'occupied'),
                        # ('room_id.capacity', '=', capacity)
                    ])
                    print(reservline_ids)

                    if reservline_ids:
                        room_reserv = room.search([
                            ('id', '!=', reservline_ids.room_id.id),
                            ('status', '!=', 'occupied')
                        ])
                        print('1')
                        print(room_reserv)
                        return room_reserv
                    else:
                        room_reserv = room.search([])
                        print('2')
                        print(room_reserv)
                        return room_reserv
        return True
