# See LICENSE file for full copyright and licensing details.

{
    "name": "Hotel Reservation Management",
    "version": "13.0.1.0.0",
    "author": "Odoo Community Association (OCA), Serpent Consulting \
                Services Pvt. Ltd., Odoo S.A.",
    "category": "Generic Modules/Hotel Reservation",
    "license": "AGPL-3",
    "summary": "Manages Guest Reservation & displays Reservation Summary",
    "website": "https://github.com/OCA/vertical-hotel/",
    "depends": ["hotel", "stock", "mail", "website", "hotel_restaurant","hotel_housekeeping"],
    "data": [
        "security/ir.model.access.csv",
        #data
        "data/website_data.xml",
        "data/hotel_scheduler.xml",
        "data/hotel_reservation_sequence.xml",
        "data/email_template_view.xml",
        #views
        "views/hotel_reservation_view.xml",
        "views/assets.xml",
        "views/res_config_settings.xml",
        "views/hotel_room.xml",
        "views/res_partner_view.xml",
        "views/hotel_reservation_line_view.xml",
        "views/hotel_foods_view.xml",
        #template
        "template/main_layaout.xml",
        "template/home_reservation.xml",
        #reports
        "report/checkin_report_template.xml",
        "report/checkout_report_template.xml",
        "report/room_max_report_template.xml",
        "report/hotel_reservation_report_template.xml",
        "report/report_view.xml",
        #Wizards
        "wizards/hotel_reservation_wizard.xml",
    ],
    "demo": ["demo/hotel_reservation_data.xml"],
    "qweb": ["static/src/xml/hotel_room_summary.xml"],
    "external_dependencies": {"python": ["dateutil"]},
    "installable": True,
}
