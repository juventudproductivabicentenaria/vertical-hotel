# See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class HotelHousekeeping(models.Model):

    _name = "hotel.housekeeping"
    _description = "Hotel Housekeeping"
    _rec_name = "code"
    
    code = fields.Char(string="Codigo", readonly=True, default="New")


    current_date = fields.Date(
        "Fecha de solicitud",
        required=True,
        index=True,
        states={"done": [("readonly", True)]},
        default=fields.Date.today,
    )
    clean_type = fields.Many2one('clean.type',
        string="Clean Type",
        required=True,
        states={"done": [("readonly", True)]},
    )
    room_id = fields.Many2one(
        "hotel.room",
        "Room No",
        # required=True,
        states={"done": [("readonly", True)]},
        index=True,
    )
    activity_line_ids = fields.One2many(
        "hotel.housekeeping.activities",
        "housekeeping_id",
        "Activities",
        states={"done": [("readonly", True)]},
        help="Detail of housekeeping \
                                        activities",
    )

    inspector_id = fields.Many2one(
        "res.users",
        "Inspector",
        states={"done": [("readonly", True)]},
    )
    inspect_date_time = fields.Datetime(
        "Inspect Date Time",
        states={"done": [("readonly", True)]},
    )
    quality = fields.Selection(
        [
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("average", "Average"),
            ("bad", "Bad"),
            ("ok", "Ok"),
        ],
        "Quality",
        states={"done": [("readonly", True)]},
        help="Inspector inspect the room and mark \
                                as Excellent, Average, Bad, Good or Ok. ",
    )
    state = fields.Selection(
        [
            ("inspect", "Inspect"),
            ("dirty", "Dirty"),
            ("clean", "Clean"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        "State",
        states={"done": [("readonly", True)]},
        required=True,
        readonly=True,
        default="inspect",
    )
    
    @api.model
    def create(self, vals):
        vals["code"] = self.env["ir.sequence"].next_by_code("hotel.housekeeping") or "New"
        res = super(HotelHousekeeping, self).create(vals)
        return res

    @api.onchange('clean_type')
    def onchange_clean_type(self):
        if self.clean_type:
            self.activity_line_ids.unlink()
            if self.clean_type.clean_activity_line_ids:
                print(self.clean_type.clean_activity_line_ids)
                for line in self.clean_type.clean_activity_line_ids:
                    self.activity_line_ids.create({
                        'activity_id': line.activity_id.id,
                        'clean_type': self.clean_type.id,
                        'housekeeping_id': self.id
                        })
                
    
    def action_set_to_dirty(self):
        """
        This method is used to change the state
        to dirty of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "dirty", "quality": False})
        # self.activity_line_ids.write({"is_clean": False, "is_dirty": True})

    def cancel_activitys(self):
        if self.inspector_id and self.env.user != self.inspector_id:
            raise ValidationError(_('Solo el inspector puede realizar esta accion'))
        if self.activity_line_ids:
            for activity in self.activity_line_ids:
                activity.write({'state': 'cancel'})

    def room_done(self):
        """
        This method is used to change the state
        to done of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        if not self.quality:
            raise ValidationError(_("Please update quality of work!"))
        self.write({"state": "done"})

    def room_inspect(self):
        """
        This method is used to change the state
        to inspect of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "inspect", "quality": False})

    def verify_activitys(self):
        if self.inspector_id and self.env.user != self.inspector_id:
            raise ValidationError(_('Solo el inspector puede realizar esta accion'))
            
        if self.activity_line_ids:
            for activity in self.activity_line_ids:
                activity.write({'state': 'done'})
