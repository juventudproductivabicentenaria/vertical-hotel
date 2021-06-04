import json

from odoo import http
from odoo.http import request
import datetime


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
        #
        # data = request.env['ProjectName.TableName'].sudo().search([("id", "=", int(Var))])
        #
        # if data:
        #     values['success'] = True
        #     values['return'] = "Something"
        # else:
        #     values['success'] = False
        #     values['error_code'] = 1
        #     values['error_data'] = 'No data found!'

        # return json.dumps(values)
        return request.render('hotel_reservation.reservation', values)
        # return values

    @http.route(['/reservation/boton_reservation'], methods=['POST'], type="http", auth="public", website=True, )
    def reservation_boton(self, **post):
        print('reservation')
        print('reservation')
        print('reservation')
        print(post)
        hotel_reservation = request.env['hotel.reservation'].sudo().search([])
        values = {
            'reservation_id': hotel_reservation
        }
        print(values)
        #
        # data = request.env['ProjectName.TableName'].sudo().search([("id", "=", int(Var))])
        #
        # if data:
        #     values['success'] = True
        #     values['return'] = "Something"
        # else:
        #     values['success'] = False
        #     values['error_code'] = 1
        #     values['error_data'] = 'No data found!'

        # return json.dumps(values)
        return request.render('hotel_reservation.reservation', values)
        # return values
