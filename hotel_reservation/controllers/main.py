import json
import logging

from odoo import http
from odoo.http import request
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)
try:
    import pytz
except (ImportError, IOError) as err:
    _logger.debug(err)


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
                'room_amenities': [' '+ amenities.name for amenities in room.room_amenities],
            })

        data = {'rooms_list': rooms}
        print(data)
        # return request.make_response(res)
        return data
