from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'
    _description = 'Description'

    request_id = fields.Many2one(
        comodel_name='maintenance.request',
        string='Maintenance Request',
        required=False)

    equipment_id = fields.Many2one(
        comodel_name='maintenance.equipment',
        string='Equipment',
        required=False)
