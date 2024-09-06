# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError



class HotelHousekeepingActivities(models.Model):
    _name = "hotel.housekeeping.activities"
    _description = "Housekeeping Activities"
    _rec_name = "code"

    code = fields.Char(string="Codigo", readonly=True, default="New")
    housekeeping_id = fields.Many2one("hotel.housekeeping", "Reservation")
    room_id = fields.Many2one("hotel.room", "habitacion", readonly=True, related='housekeeping_id.room_id', store=True)
    inspector_id = fields.Many2one("res.users", "Inspector", readonly=True, related='housekeeping_id.inspector_id', store=True)
    today_date = fields.Date("fecha de solicitud", related='housekeeping_id.current_date', readonly=True)
    activity_id = fields.Many2one("hotel.activity", "Housekeeping Activity")
    user_id = fields.Many2one("res.users", "Encargado", required=False)
    clean_start_time = fields.Datetime("Clean Start Time", required=False)
    clean_end_time = fields.Datetime("Clean End Time", required=False)
    clean_type = fields.Many2one("clean.type", "Tipo de limpieza", required=False)
    
    done_activity = fields.Boolean(
        "Realizada",
        readonly=True,
        help="Marcar como realizada la actividad",
    )
   
    # no_done_activity = fields.Boolean(
    #     "No realizada",
    #     help="Marcar como no realizada la actividad",
    # )

    parent_state = fields.Selection([
            ("inspect", "Inspect"),
            ("in_process", "En proceso"),
            # ("clean", "Clean"),
            ("done", "Realizada"),
            ("cancel", "Cancelled"),
        ], "State",
        related='housekeeping_id.state'
    )

    state = fields.Selection([
        ('draft', 'Sin verificar'),
        # ('done', 'Realizada'),
        ("not_verify", "No verificada"),
        ('verify', 'Verificado'),
        ('cancel', 'Cancelado'),
    ], string='Estado', readonly=True, default='draft')
    

    # @api.onchange('done_activity')
    # def onchange_state_housekeeping_id(self):
    #     if self.housekeeping_id and self.housekeeping_id.state == 'inspect':
    #         self.housekeeping_id.state = 'in_process'
    #     pass 
    

    @api.model
    def create(self, vals):
        if not vals.get("code") or vals.get("code") == "New":
            vals["code"] = self.env["ir.sequence"].next_by_code("hotel.housekeeping.activities") or "New"
        res = super(HotelHousekeepingActivities, self).create(vals)
        return res
    
    
    def verifyActivity(self):
        for activity in self:
            if activity.inspector_id and self.env.user != activity.inspector_id:
                raise ValidationError(_('Solo el inspector puede realizar esta accion'))
            activity.write({'state': 'verify'})

    def draftActivity(self):
        for activity in self:
            if activity.inspector_id and self.env.user != activity.inspector_id and activity.user_id and self.env.user != activity.user_id:
                raise ValidationError(_('Solo el asignado puede modificar la actividad o su Inspector'))
            activity.write({'state': 'draft'})
            activity.write({'done_activity': 'False'})

    def doneActivity(self):
        for activity in self:
            if activity.inspector_id and self.env.user != activity.inspector_id and activity.user_id and self.env.user != activity.user_id:
                raise ValidationError(_('Solo el asignado puede modificar la actividad o su Inspector'))
            activity.sudo().write({'done_activity': True})

    def canceldoneActivity(self):
        for activity in self:
            if activity.inspector_id and self.env.user != activity.inspector_id and activity.user_id and self.env.user != activity.user_id:
                raise ValidationError(_('Solo el asignado puede modificar la actividad o su Inspector'))
            activity.sudo().write({'done_activity': False})

    def cancelActivity(self):
        for activity in self:
            if activity.inspector_id and self.env.user != activity.inspector_id:
                raise ValidationError(_('Solo el inspector puede realizar esta accion'))
            activity.write({'state': 'cancel'})
                

    @api.constrains("clean_start_time", "clean_end_time")
    def _check_clean_start_time(self):
        """
        This method is used to validate the clean_start_time and
        clean_end_time.
        ---------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        for activity in self:
            if activity.clean_start_time and activity.clean_end_time:
                if activity.clean_start_time >= activity.clean_end_time:
                    raise ValidationError(
                        _("Start Date Should be less than the End Date!")
                    )

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        res = super().default_get(fields)
        if self._context.get("room_id", False):
            res.update({"room_id": self._context["room_id"]})
        if self._context.get("today_date", False):
            res.update({"today_date": self._context["today_date"]})
        return res
