import json
import logging
import pytz
from odoo import http
from odoo.http import request
from odoo import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.exceptions import ValidationError,UserError
from datetime import date, timedelta, time, datetime
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
        if not request.session.uid:
            return http.redirect_with_hash("/web/login")
        
        hotel_reservation = request.env['hotel.reservation'].sudo().search([])
        values = {
            'reservation_id': hotel_reservation
        }
        return request.render('hotel_reservation.hotel_search_reservation', values)

    @http.route('/reservation/date_updated', type='json', auth='public', website=True)
    def date_updated(self, **kwargs):

        # date_from = datetime.today() - relativedelta(hours=4) + relativedelta(days=1)
        # date_to = date_from + relativedelta(days=1)
        date_from = date.today() - relativedelta(hours=4) + relativedelta(days=1)
        date_to = date_from + relativedelta(days=1)
        res = {'date_from': date_from.date(),
                'date_to': date_to.date()
                }

        return res
    @http.route('/search_person', type='json', auth='public')
    def search_person(self, **kwargs):
        partner_ci = kwargs["partner_ci"]
        ResPartner = request.env['res.partner']
        if not partner_ci:
            return {'no_id': 'Falta la CI del partner'}

        try:
            partner = ResPartner.search([('vat', '=', partner_ci)])
            if not partner:
                return {'missing': 'No se encontró el partner'}

            # Obtenemos el campo que queremos devolver
            return {
                "id": partner.id,
                "name": partner.name,
                "email": partner.email,
                "phone": partner.phone
            }

        except Exception as e:
            return json.dumps({'error': str(e)})
        
    @http.route('/reservation/search_reservation', type='json', auth="public", website=True, sitemap=False)
    def search_reservation(self, access_token=None, revive='', **kwargs):
        # main_ci = kwargs["main_ci"]
        # main_email = kwargs["main_email"]
        # main_phone = kwargs["main_phone"]
        date_from = kwargs['date_from']
        date_until = kwargs['date_until']   
        adults = kwargs['adults']
        ninos = kwargs['ninos']
        user_id = request.env.user
        ResPartner = request.env['res.partner']
        HotelReservation = request.env['hotel.reservation'].sudo()
        HotelReservationLine = request.env['hotel_reservation.line'].sudo()
        HotelFood = request.env['hotel.foods'].sudo()
        HotelTransport = request.env['hotel.transport'].sudo()
        warehouse_id = user_id.company_id.warehouse_id.id
        if warehouse_id == False:
            warehouse_id = 1
        hotel_reservation = request.env['reserve.room'].sudo().reservation_room(date_from, date_until, adults, ninos, 0)
        if not hotel_reservation:
            return {
                "error_validation": True,
                "title_error": "Error al crear la reservación",
                "content_error": "No se encontro ninguna habitacion disponible entre las fechas seleccionadas.",
                }
        reservation_partner_ids = []
        total_children = 0
        if "full_data" in kwargs:
            _logger.info(kwargs["full_data"])

            
            new_reservation = HotelReservation.create({
                "partner_id": user_id.partner_id.id,
                "partner_invoice_id": user_id.partner_id.id,
                "partner_order_id": user_id.partner_id.id,
                "partner_shipping_id": user_id.partner_id.id,
                "checkin": date_from,
                "checkout": date_until,
                "warehouse_id": warehouse_id,
                "adults": adults,
                "children": ninos,
                "token": tools.default_hash()
            })

            reservation_line_partners = []
            for data in kwargs["full_data"]:
                partner = ResPartner.search([('vat', '=', data["vat"])])
                if partner:
                    reservation_partner_ids.append( {
                        "vat": partner.vat,
                        "name": partner.name,
                        "email": partner.email,
                        "phone": partner.phone,
                    })
                children_ids = []
                if not partner:
                    partner_vals = {   
                        "vat": data["vat"],
                        "name": data["name"],
                        "email": data["email"],
                        "phone": data["phone"],
                    }
                    new_partner = ResPartner.create({partner_vals})
                    reservation_partner_ids.append(partner_vals)

                    if 'childrens' in data and data["second_vat"] == "":
                        for chil in data['childrens']:
                            new_children = ResPartner.create({
                                "name": chil["nombre"],
                                "phone": chil["telefono"],
                            })
                            children_ids.append(new_children.id)
                            total_children += 1
                            
                        reservation_line = HotelReservationLine.create({
                            "line_id": new_reservation.id,
                            "is_son": True if len(children_ids) > 0 else False,
                            "is_couple": False,
                            "partner_id": new_partner.id,
                            "checkin": new_reservation.checkin,
                            "checkout": new_reservation.checkout,
                            "children_ids": children_ids,
                            "include_room": data["include_room"],
                            "institution_from": data["institution_name"],
                        })
                                                
                        
                    elif 'childrens' in data and data["second_vat"] != "":
                        for chil in data['childrens']:
                            new_children = ResPartner.create({
                                "name": chil["nombre"],
                                "phone": chil["telefono"],
                            })
                            children_ids.append(new_children.id)
                            total_children += 1
                            
                        partner_2 = ResPartner.search([('vat', '=', data["second_vat"])])
                        if partner_2:
                            reservation_partner_ids.append( {
                                "vat": partner_2.vat,
                                "name": partner_2.name,
                                "email": partner_2.email,
                                "phone": partner_2.phone,
                            })
                        if not partner_2:
                            partner_vals = {
                                "vat": data["second_vat"],
                                "name": data["second_name"],
                                "email": data["second_email"],
                                "phone": data["second_phone"],
                            }
                            new_partner_2 = ResPartner.create({partner_vals})
                            reservation_partner_ids.append(partner_vals)
                            
                            reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": True if len(children_ids) > 0 else False,
                                "is_couple": True,
                                "partner_id": new_partner.id,
                                "couple_id": new_partner_2.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "children_ids": children_ids,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                            children_ids = []
                            
                        else:
                            reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": True if len(children_ids) > 0 else False,
                                "is_couple": True,
                                "partner_id": new_partner.id,
                                "couple_id": partner_2.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "children_ids": children_ids,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                            children_ids = []
                            
                    elif not 'childrens' in data and data["second_vat"] == "":
                        reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": False,
                                "is_couple": False,
                                "partner_id": new_partner.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                        
                    elif not 'childrens' in data and data["second_vat"] != "":
                        partner_2 = ResPartner.search([('vat', '=', data["second_vat"])])
                        if partner_2:
                            reservation_partner_ids.append( {
                                "vat": partner_2.vat,
                                "name": partner_2.name,
                                "email": partner_2.email,
                                "phone": partner_2.phone,
                            })
                        
                        if not partner_2:
                            partner_vals = {
                                "vat": data["second_vat"],
                                "name": data["second_name"],
                                "email": data["second_email"],
                                "phone": data["second_phone"],
                            }
                            new_partner_2 = ResPartner.create({partner_vals})
                            reservation_partner_ids.append(partner_vals)
                            reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": False,
                                "is_couple": True,
                                "partner_id": new_partner.id,
                                "couple_id": new_partner_2.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                            children_ids = []
                            
                        else:
                            reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": False,
                                "is_couple": True,
                                "partner_id": new_partner.id,
                                "couple_id": partner_2.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                            children_ids = []
                            
                    if data["include_food"]:
                        if data.get("breakfast"):
                            HotelFood.create({
                                "dates": data["breakfast"]["from_break"],
                                "hotel_reservation": new_reservation.id,
                                "state": "breakfast",
                                "partner_id": new_partner.id
                            })
                            
                        if data.get("lunch"):
                            HotelFood.create({
                                "dates": data["lunch"]["from_lunch"],
                                "hotel_reservation": new_reservation.id,
                                "state": "lunch",
                                "partner_id": new_partner.id
                            })
                            
                        if data.get("dinner"):
                            HotelFood.create({
                                "dates": data["dinner"]["from_dinner"],
                                "hotel_reservation": new_reservation.id,
                                "state": "dinner",
                                "partner_id": new_partner.id
                            })
                            
                    if data["include_transport"] == True:
                        HotelTransport.create({
                            "hotel_reservation": new_reservation.id,
                            "move_from": data["origen"],
                            "move_to": data["destiny"],
                            "partner_id": new_partner.id
                        })
                else:
                    if 'childrens' in data and data["second_vat"] == "":
                        for chil in data['childrens']:
                            new_children = ResPartner.create({
                                "name": chil["nombre"],
                                "phone": chil["telefono"],
                            })
                            children_ids.append(new_children.id)
                            total_children += 1
                            
                        reservation_line = HotelReservationLine.create({
                            "line_id": new_reservation.id,
                            "is_son": True if len(children_ids) > 0 else False,
                            "is_couple": False,
                            "partner_id": partner.id,
                            "checkin": new_reservation.checkin,
                            "checkout": new_reservation.checkout,
                            "children_ids": children_ids,
                            "include_room": data["include_room"],
                            "institution_from": data["institution_name"],
                        })                   
                        
                    elif 'childrens' in data and data["second_vat"] != "":
                        for chil in data['childrens']:
                            new_children = ResPartner.create({
                                "name": chil["nombre"],
                                "phone": chil["telefono"],
                            })
                            children_ids.append(new_children.id)
                            total_children += 1
                            
                        partner_2 = ResPartner.search([('vat', '=', data["second_vat"])])
                        if partner_2:
                            reservation_partner_ids.append( {
                                "vat": partner_2.vat,
                                "name": partner_2.name,
                                "email": partner_2.email,
                                "phone": partner_2.phone,
                            })
                        
                        if not partner_2:
                            partner_vals = {
                                "vat": data["second_vat"],
                                "name": data["second_name"],
                                "email": data["second_email"],
                                "phone": data["second_phone"],
                            }
                            new_partner_2 = ResPartner.create({partner_vals})
                            reservation_partner_ids.append(partner_vals)

                            reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": True if len(children_ids) > 0 else False,
                                "is_couple": True,
                                "partner_id": partner.id,
                                "couple_id": new_partner_2.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "children_ids": children_ids,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                            children_ids = []
                            
                        else:
                            print(data)
                            reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": True if len(children_ids) > 0 else False,
                                "is_couple": True,
                                "partner_id": partner.id,
                                "couple_id": partner_2.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "children_ids": children_ids,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                            children_ids = []
                            
                            
                    elif not 'childrens' in data and data["second_vat"] == "":
                        reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": False,
                                "is_couple": False,
                                "partner_id": partner.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                        
                    elif not 'childrens' in data and data["second_vat"] != "":
                        partner_2 = ResPartner.search([('vat', '=', data["second_vat"])])
                        if partner_2:
                            reservation_partner_ids.append( {
                                "vat": partner_2.vat,
                                "name": partner_2.name,
                                "email": partner_2.email,
                                "phone": partner_2.phone,
                            })
                        if not partner_2:
                            partner_vals = {
                                "vat": data["second_vat"],
                                "name": data["second_name"],
                                "email": data["second_email"],
                                "phone": data["second_phone"],
                            }
                            new_partner_2 = ResPartner.create({partner_vals})
                            reservation_partner_ids.append(partner_vals)

                            reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": False,
                                "is_couple": True,
                                "partner_id": partner.id,
                                "couple_id": new_partner_2.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                            children_ids = []
                            
                        else:
                            reservation_line = HotelReservationLine.create({
                                "line_id": new_reservation.id,
                                "is_son": False,
                                "is_couple": True,
                                "partner_id": partner.id,
                                "couple_id": partner_2.id,
                                "checkin": new_reservation.checkin,
                                "checkout": new_reservation.checkout,
                                "include_room": data["include_room"],
                                "institution_from": data["institution_name"],
                            })
                            children_ids = []
                            
                    if data["include_food"]:
                        if data.get("breakfast"):
                            HotelFood.create({
                                "dates": data["breakfast"]["from_break"],
                                "hotel_reservation": new_reservation.id,
                                "state": "breakfast",
                                "partner_id": partner.id
                            })
                            
                        if data.get("lunch"):
                            HotelFood.create({
                                "dates": data["lunch"]["from_lunch"],
                                "hotel_reservation": new_reservation.id,
                                "state": "lunch",
                                "partner_id": partner.id
                            })
                            
                        if data.get("dinner"):
                            HotelFood.create({
                                "dates": data["dinner"]["from_dinner"],
                                "hotel_reservation": new_reservation.id,
                                "state": "dinner",
                                "partner_id": partner.id
                            })
                    
                    if data["include_transport"] == True:
                        
                        HotelTransport.create({
                            "hotel_reservation": new_reservation.id,
                            "move_from": data["origen"],
                            "move_to": data["destiny"],
                            "partner_id": partner.id
                        })
                        
            return {"data": "ok"}
        # institution_visit = kwargs["institution_name"]
        # main_name = kwargs["main_name"]
        
        children_ids = []
        warehouse_id = user_id.company_id.warehouse_id.id
        if warehouse_id == False:
            warehouse_id = 1
        new_reservation = HotelReservation.create({
            "partner_id": user_id.partner_id.id,
            "partner_invoice_id": user_id.partner_id.id,
            "partner_order_id": user_id.partner_id.id,
            "partner_shipping_id": user_id.partner_id.id,
            "checkin": date_from,
            "checkout": date_until,
            "warehouse_id": warehouse_id,
            "adults": adults,
            "children": ninos,
            "token": tools.default_hash()
        })
        
        for chil in kwargs['children_list']:
            new_children = ResPartner.create({
                "name": chil["nombre"],
                "phone": chil["telefono"],
            })
            children_ids.append(new_children.id)
            total_children += 1
            
        reservation_line_partners = []

        vats = kwargs["vats"]
        for i in range(0, len(vats)):
            partner = ResPartner.search([('vat', '=', vats[i])])
            if partner:
                reservation_partner_ids.append( {
                    "vat": partner.vat,
                    "name": partner.name,
                    "email": partner.email,
                    "phone": partner.phone,
                })
                reservation_line_partners.append(partner)
            else:
                partner_vals = {
                    "vat": vats[i],
                    "name": kwargs["names"][i],
                    "email": kwargs["emails"][i],
                    "phone": kwargs["phones"][i],
                }
                new_partners = ResPartner.create({partner_vals})
                reservation_partner_ids.append(partner_vals)
                reservation_line_partners.append(new_partners)
        
        if len(reservation_line_partners) == 1 and len(kwargs["children_list"]) == 0:
            reservation_line = HotelReservationLine.create({
                "line_id": new_reservation.id,
                "is_son": False,
                "is_couple": False,
                "partner_id": reservation_line_partners[0].id,
                "checkin": new_reservation.checkin,
                "checkout": new_reservation.checkout,
                "include_room": kwargs["include_room"],
                "institution_from": kwargs["institution_name"],
                # "hotel_room_id": room.id
            })
            
        elif len(reservation_line_partners) == 1 and len(kwargs["children_list"]) > 0:
            reservation_line = HotelReservationLine.create({
                "line_id": new_reservation.id,
                "is_son": True if len(children_ids) > 0 else False,
                "is_couple": False,
                "partner_id": reservation_line_partners[0].id,
                "checkin": new_reservation.checkin,
                "checkout": new_reservation.checkout,
                'children_ids': children_ids,
                "include_room": kwargs["include_room"],
                "institution_from": kwargs["institution_name"],
                # "hotel_room_id": room.id
            })
            
        elif len(reservation_line_partners) == 2 and len(kwargs["children_list"]) == 0:
            reservation_line = HotelReservationLine.create({
                "line_id": new_reservation.id,
                "is_son": False,
                "is_couple": True,
                "partner_id": reservation_line_partners[0].id,
                "couple_id": reservation_line_partners[1].id,
                "checkin": new_reservation.checkin,
                "checkout": new_reservation.checkout,
                "include_room": kwargs["include_room"],
                "institution_from": kwargs["institution_name"],
                # "hotel_room_id": room.id
            })
            
        elif len(reservation_line_partners) == 2 and len(kwargs["children_list"]) > 0:
            reservation_line = HotelReservationLine.create({
                "line_id": new_reservation.id,
                "is_son": True if len(children_ids) > 0 else False,
                "is_couple": True,
                "partner_id": reservation_line_partners[0].id,
                "couple_id": reservation_line_partners[1].id,
                "checkin": new_reservation.checkin,
                "checkout": new_reservation.checkout,
                'children_ids': children_ids,
                "include_room": kwargs["include_room"],
                "institution_from": kwargs["institution_name"],
                # "hotel_room_id": room.id
            })
            
        if kwargs["include_food"]:
            if kwargs["breakfast"]:
                HotelFood.create({
                    "dates": kwargs["breakfast"]["from_break"],
                    "hotel_reservation": new_reservation.id,
                    "state": "breakfast",
                    "partner_id": reservation_line_partners[0].id
                })
                
            if kwargs.get("lunch"):
                HotelFood.create({
                    "dates": kwargs["lunch"]["from_lunch"],
                    "hotel_reservation": new_reservation.id,
                    "state": "lunch",
                    "partner_id": reservation_line_partners[0].id
                })
                
            if kwargs.get("dinner"):
                HotelFood.create({
                    "dates": kwargs["dinner"]["from_dinner"],
                    "hotel_reservation": new_reservation.id,
                    "state": "dinner",
                    "partner_id": reservation_line_partners[0].id
                })
                
        if kwargs["include_transport"] == True:
            HotelTransport.create({
                "hotel_reservation": new_reservation.id,
                "move_from": kwargs["origen"],
                "move_to": kwargs["destiny"],
                "partner_id": reservation_line_partners[0].id
            })
        # Reservation created successfully
        _logger.info("Reservation created!")
        _logger.info(new_reservation.id)
        result = {
            "reserved": True,
            "reservation_id": new_reservation.id,
            "token": new_reservation.token,
            "code": new_reservation.reservation_no,
            "date_order": new_reservation.date_order.strftime("%d-%m-%Y %H:%M:%S"),
            "checkin": new_reservation.checkin.strftime("%d-%m-%Y %H:%M:%S"),
            "checkout": new_reservation.checkout.strftime("%d-%m-%Y %H:%M:%S"),
            "partner_id": new_reservation.partner_id.name,
            "reservation_partner_ids": reservation_partner_ids,
            "total_children": total_children,
        }
        return result

    @http.route('/reservation/reserved_rooms', type='json', auth="public", website=True, sitemap=False)
    def reserved_rooms(self, access_token=None, revive='', **post):
        # HotelReservation = request.env['hotel.reservation'].sudo()
        # HotelReservationOrden = request.env['hotel.reservation.order'].sudo()
        # HotelReservationLine = request.env['hotel_reservation.line'].sudo()
        # HotelMenucard = request.env['hotel.menucard'].sudo()
        # HotelRestaurantOrderList = request.env['hotel.restaurant.order.list'].sudo()
        # adults = int(post['adults'])
        # rooms_limit = int(post['rooms'])
        # foodList = post['foodList']
        # capacity = 0
        # print("post")
        # print("post")
        # print(post)
        # print(foodList)
        # date_from = post['date_from']
        # date_to = post['date_until']
   
        ids = post['ids']
        # id_room = 0
        # list_ids = []
        # ninos = int(post['ninos'])
        user_id = request.env.user
        _logger.info(user_id.partner_id)
        _logger.info(ids)
        return {"data": user_id.partner_id}
        partner_id = user_id.partner_id
        # pricelist_id = request.env['product.pricelist'].sudo().search([])
        reservation_id = 0
        room = request.env['hotel.room']
        room_name = []
        rooms_id = []
        reservation = False
        orden_ids = []
        d_from = ''
        d_today = ''
        today = (datetime.today() - relativedelta(hours=4))
        warehouse_id = user_id.company_id.warehouse_id
        tz = pytz.timezone(warehouse_id.tz)
        values = {}
        if date_from and date_to:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            date_from = tz.normalize(tz.localize(date_from)).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            date_to = tz.normalize(tz.localize(date_to)).astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
            today = today.strftime("%Y-%m-%d %H:%M:%S")
        for date in date_from:
            d_from += date
        for date in today:
            d_today += date

        rooms = room.sudo().search([('token', 'in', ids)],limit=rooms_limit)
          
        values.update({
            "partner_id": partner_id.id,
            "partner_invoice_id": partner_id.id,
            "partner_order_id": partner_id.id,
            "partner_shipping_id": partner_id.id,
            "checkin": date_from,
            "checkout": date_to,
            "warehouse_id": warehouse_id.id,
            # "pricelist_id": pricelist_id.id,
            "adults": adults,
            "children": ninos,
            "token": tools.default_hash(),
        })
        print("post.get('reserve_room')")
        print(post.get('reserve_room'))
        print("post.get('reserve_foom')")
        print(post.get('reserve_food'))
        if post.get('reserve_room'):
            reservation = HotelReservation.create(values)
        if post.get('reserve_food'):
            print("foodList")
            print("foodList")
            print("foodList")
            print(foodList)
            for food in foodList:
                print("food")
                print("food")
                print(food)
                values_orden = {}
                order_list_ids = []
                formato = "%Y-%m-%d"  # Format of the date string
                values_orden.update({
                    "is_folio": False,
                    "order_date": datetime.strptime(food['date'],formato),
                })
                if post.get('reserve_room') and reservation:
                    values_orden['is_folio'] = True
                    values_orden['reservation_room_id'] = reservation.id
                orden_id = HotelReservationOrden.create(values_orden)
                print("orden_id")
                print("orden_id")
                print(orden_id)
                print(food['order'])
                for orden in food['order']:
                    if orden.get('quantity') and int(orden['quantity']) > 0:
                        values_orden_line = {
                            'reservation_order_id':orden_id.id,
                            'menucard_id':HotelMenucard.search([('name','=',orden['code'])]).id,
                            'item_qty':orden['quantity'],
                        }
                        line = HotelRestaurantOrderList.create(values_orden_line)
                        print("line")
                        print("line")
                        print(line)
                        order_list_ids.append(line.id)
                orden_id.order_list_ids = [(6, 0, order_list_ids)]
                print("order_list_ids")
                print("order_list_ids")
                print(order_list_ids)
        if rooms:
            for room in rooms:
                capacity += room.capacity
                val = {
                    "line_id": reservation.id,
                    "hotel_room_id": room.id,
                    "partner_id": partner_id.id,
                    "checkin": date_from,
                    "checkout": date_to,
                }
                reservationline = HotelReservationLine.create(val)
                rooms_id.append(reservationline.id)
            reservation.reservation_line_ids = [(6, 0, rooms_id)]

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
        today = datetime.today()

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
