from odoo import fields, models, api


class AccountChecklist(models.Model):
    _name = 'account.checklist'
    _description = 'Description'

    name = fields.Char(
        string='Name',
        required=False)

    description = fields.Text(
        string="Description",
        required=False)

    steps_ids = fields.One2many(
        comodel_name='account.checklist.steps',
        inverse_name='checklist_id',
        string='Steps',
        required=False)
