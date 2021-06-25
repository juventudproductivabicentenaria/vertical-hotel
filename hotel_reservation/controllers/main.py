import json
import logging
import pytz

from odoo import http
from odoo.http import request
from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as dt
import datetime
from datetime import date, timedelta, time
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)

DEFAULT_TIME_FORMAT = '%H:%M:%S'


class Website(http.Controller):

    @http.route(['/reservation'], type="http", auth="public", website=True,)
    def reservation(self, **post):
        print('reservation')
        print('reservation')
        print('reservation')
        print(post)
        hotel_reservation = request.env['hotel.reservation'].sudo().search([])
        values = {
            'reservation_id': hotel_reservation
        }
        print(values)
        return request.render('hotel_reservation.hotel_search_reservation', values)
        # return values

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
        # print(room)

        # res =  {'rooms_list': room}

        for room in hotel_reservation:
            rooms.append({
                'name': room.name,
                'id': room.id,
                'image_1920': room.image_1920,
                'capacity': room.capacity,
                'room_amenities': [' '+ amenities.name for amenities in room.room_amenities],
            })

        data = {'rooms_list': rooms}
        print(data)
        # return request.make_response(res)
        return data

    @http.route('/reservation/reserved_rooms', type='json', auth="public", website=True, sitemap=False)
    def reserved_rooms(self, access_token=None, revive='', **kwargs):

        adults = int(kwargs['adults'])
        date_from = kwargs['date_from'] + ' 14:00:00'
        date_to = kwargs['date_until'] + ' 12:00:00'
        hotel_reservation = request.env['hotel.reservation']
        ids = kwargs['ids']
        id_room = 0
        ninos = int(kwargs['ninos'])
        user_id = request.env.user
        partner_id = user_id.partner_id
        pricelist_id = request.env['product.pricelist'].sudo().search([])
        reservation_no = ''
        room = request.env['hotel.room']
        warehouse_id = user_id.company_id.warehouse_id
        tz = pytz.timezone(warehouse_id.tz)

        if date_from and date_to:
            date_from = datetime.datetime.strptime(date_from, dt)
            date_to = datetime.datetime.strptime(date_to, dt)
            date_from = tz.normalize(tz.localize(date_from)).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            date_to = tz.normalize(tz.localize(date_to)).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")

        for id in ids:
            id_room = int(id)

        rooms = room.browse(id_room)

        values = {
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
            "reservation_line_ids": [
                        (
                            0,
                            0,
                            {
                                "reserve": [(6, 0, [rooms.id])],
                                "name": (
                                    rooms and rooms.name or ""
                                ),
                            },
                        )
            ],
        }

        print(values)
        # print (ooooo)

        if not adults:
            print("La cantidad de adultos debe ser mayor a 0")
            return

        # reservation = hotel_reservation.create(values)

        # if reservation:
        #     reservation_no = reservation.reservation_no

        # data = {'reservation_no': reservation_no}
        data = {'reservation_no': [98]}

        print('data')
        
        return data

    # @http.route(['/reserved/<int:reservation_id>'], type='http', auth="public", website=True,)
    @http.route(['/reserved/<model("hotel.reservation"):reservation>'], type='http', auth="public", website=True)
    def reservado(self,  reservation):
        print('reservation_no')
        print('reservation_no')
        print(reservation.reservation_no)

        try:
            # return json.dumps({"result":True})
            return request.render("hotel_reservation.room_reserved", {'reservations': reservation})
        except:
            pass
