# See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError

class CleanType(models.Model):
    _name = "clean.type"
    _description = "Clean Type"

    name = fields.Char(required=True)


    active = fields.Boolean(default=True)

    clean_activity_line_ids = fields.One2many(
        "clean.activity.line",
        "clean_type_id",
        "Actividades de tipo de limpieza",
        help="Actividades de tipo de limpieza",
    )

    # @api.model
    # def create(self, values):
    #     if not values.get("code"):
    #         values["code"] = values["name"].replace(" ", "-").lower()
    #     result = super(CleanType, self).create(values)
    #     return result

    _sql_constraints = [
        (
            "name_unique",
            "unique(name)",
            "El nombre debe ser único",
        ),
    ]
class CleanType(models.Model):
    _name = "clean.activity.line"
    _description = "Clean Activity"

    # name = fields.Char(required=True)

    clean_type_id = fields.Many2one(
        "clean.type",
        "Tipo de limpieza",
        index=True,
    )
    activity_id = fields.Many2one(
        "hotel.activity",
        "Actividad",
        required=True,
    )
    
    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name and record.clean_type_id:
                result = self.search([
                    ('id', '!=', record.id),
                    ('name', '=', record.name),
                    ('clean_type_id', '=', record.clean_type_id.id),
                ])
                if result:
                    raise ValidationError(_('Nombre de la actividad de limpieza ya existe!'))

            
    