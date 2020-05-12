from odoo import fields, models, api


class AccountChecklistSteps(models.Model):
    _name = 'account.checklist.steps'
    _description = 'Description'

    name = fields.Char(
        string='Name',
        required=False)

    description = fields.Text(
        string="Description",
        required=False)

    checklist_id = fields.Many2one(
        comodel_name='account_checklist',
        string='Checklist',
        required=False)
