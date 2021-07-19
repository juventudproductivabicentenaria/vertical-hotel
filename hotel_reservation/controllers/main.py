import json
import logging
import pytz

from odoo import http
from odoo.http import request
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import ValidationError,UserError
import datetime
from datetime import date, timedelta, time
from dateutil.relativedelta import relativedelta
from ..models import tools


_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)

DEFAULT_TIME_FORMAT = '%H:%M:%S'


class Website(http.Controller):

    @http.route(['/'], type="http", auth="public", website=True,)
    def home_reservation(self, **post):
        return request.render('hotel_reservation.home_reservation')

    @http.route(['/reservation'], type="http", auth="public", website=True,)
    def reservation(self, **post):
        hotel_reservation = request.env['hotel.reservation'].sudo().search([])
        values = {
            'reservation_id': hotel_reservation
        }
        return request.render('hotel_reservation.hotel_search_reservation', values)

    @http.route('/reservation/date_updated', type='json', auth='public', website=True)
    def date_updated(self, **kwargs):

        date_from = date.today()
        date_to = date_from + relativedelta(days=1)
        print('type(date_to)')
        print(date_to)
        print(type(date_from))
        res = {'date_from': date_from,
                'date_to': date_to
                }

        return res

    @http.route('/reservation/search_reservation', type='json', auth="public", website=True, sitemap=False)
    def search_reservation(self, access_token=None, revive='', **kwargs):

        date_from = kwargs['date_from']
        date_until = kwargs['date_until']
        adults = kwargs['adults']
        ninos = kwargs['ninos']
        rooms = []

        hotel_reservation = request.env['reserve.room'].sudo().reservation_room(date_from, date_until, adults, ninos)

        room = hotel_reservation.read(['name', 'image_1920', 'room_amenities'])

        for room in hotel_reservation:
            rooms.append({
                'name': room.name,
                'id': room.id,
                'image_1920': room.image_1920,
                'capacity': room.capacity,
                'room_amenities': [' '+ amenities.name for amenities in room.room_amenities],
                'token': room.token
            })

        data = {'rooms_list': rooms}
        return data

    @http.route('/reservation/reserved_rooms', type='json', auth="public", website=True, sitemap=False)
    def reserved_rooms(self, access_token=None, revive='', **kwargs):

        adults = int(kwargs['adults'])
        capacity = 0
        date_from = kwargs['date_from'] + ' 14:00:00'
        date_to = kwargs['date_until'] + ' 12:00:00'
        hotel_reservation = request.env['hotel.reservation']
        ids = kwargs['ids']
        id_room = 0
        list_ids = []
        ninos = int(kwargs['ninos'])
        user_id = request.env.user
        partner_id = user_id.partner_id
        pricelist_id = request.env['product.pricelist'].sudo().search([])
        reservation_id = 0
        room = request.env['hotel.room']
        room_name = []
        rooms_id = []
        d_from = ''
        d_today = ''
        today = datetime.datetime.today()
        warehouse_id = user_id.company_id.warehouse_id
        tz = pytz.timezone(warehouse_id.tz)
        values = {}

        if date_from and date_to:
            date_from = datetime.datetime.strptime(date_from, dt)
            date_to = datetime.datetime.strptime(date_to, dt)
            date_from = tz.normalize(tz.localize(date_from)).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            date_to = tz.normalize(tz.localize(date_to)).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            today = today.strftime("%Y-%m-%d %H:%M:%S")

        for date in date_from:
            d_from += date
        for date in today:
            d_today += date

        if d_from[8:10] == d_today[8:10]:
            data = {'error_validation': 'La fecha de inicio debe ser mayor al dia de hoy.',
            }
            return data

        # for id in ids:
        #     id_room = int(id)
        #     list_ids.append(id_room)

        # rooms = room.sudo().search([('id', 'in', list_ids)])
        rooms = room.sudo().search([('token', 'in', ids)])

        if rooms:
            for room in rooms:
                id = room.id
                capacity += room.capacity
                name = room.name
                room_name.append(name)
                rooms_id.append(id)

        values.update({
            "partner_id": partner_id.id,
            "partner_invoice_id": partner_id.id,
            "partner_order_id": partner_id.id,
            "partner_shipping_id": partner_id.id,
            "checkin": date_from,
            "checkout": date_to,
            "warehouse_id": warehouse_id.id,
            "pricelist_id": pricelist_id.id,
            "adults": adults,
            "children": ninos,
            "token": tools.default_hash(),
            "reservation_line_ids": [
                        (
                            0,
                            0,
                            {
                                "reserve": [(6, 0, rooms_id)],
                                "name": (
                                    rooms and room_name or ""
                                ),
                            },
                        )
            ],
        })

        if not adults:
            data = {'error_validation': 'La cantidad de adultos debe ser mayor a 0.',
            }
            return data

        if adults > capacity:
            data = {'error_validation': 'La capacidad de la habitacion es muy baja para la cantidad de personas, \n'
             ' por favor reserve una habitacion adicional o de mayor capacidad'
            }
            return data

        reservation = hotel_reservation.create(values)
        # data = {'reservation_id': 13,
        #         'token': '59d861919bc0477807dd462dcaacba74fd0a81dd13',
        #         }


        if reservation:
            reservation_id = reservation.id
            data = {'reservation_id': reservation_id,
                    'token':reservation.token,
                    }
            return data
        else:
            return {}
        return data

    @http.route(['/reserved/<model("hotel.reservation"):reservation>'], type='http', auth="public", website=True)
    def reservado(self,  reservation, **kwargs):

        token_hash = kwargs['token']

        if reservation.token != token_hash:
            raise ValidationError(_('No puedes ver el registro'))

        if reservation.state == 'draft':
            reservation.confirm_reservation()

        values ={
            'reservations': reservation,
            'reserve': kwargs.get('reserve'),
        }

        try:
            return request.render("hotel_reservation.room_reserved", values)
        except:
            pass

    @http.route(['/reserve/list'], type="http", auth="public", website=True,)
    def reserve_list(self, **post):

        user_id = request.env.user
        partner_id = user_id.partner_id
        hotel_reservation = request.env['hotel.reservation'].sudo().search([('partner_id', '=', partner_id.id)])
        values = {}

        
        if post:
            values.update({'message': post['message']})
        
        values.update({
            'reservation_id': hotel_reservation,
        })

        return request.render('hotel_reservation.reserve_list', values)

    @http.route(['/reserve/list/<int:reserve_id>'], type="http", auth="public", website=True,)
    def cancel_reservation(self, reserve_id, **kwargs):
        hotel_reservation = request.env['hotel.reservation']
        today = datetime.datetime.today()

        if reserve_id:
            token_hash = kwargs['token']
            reservation =hotel_reservation.browse(reserve_id)

            for reserva in reservation:
                if reserva.token == token_hash:
                    if today > reservation.checkout:
                        raise ValidationError(_('No puedes cancelar la Reservación'))
                    reservation.cancel_reservation()
                    continue
                else:
                    raise ValidationError(_('No puedes cancelar la Reservación'))

        return self.reserve_list(message="Su cancelacion fue exitosa")
