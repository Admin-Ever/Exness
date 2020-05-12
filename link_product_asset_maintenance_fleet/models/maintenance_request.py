from datetime import datetime, timedelta
from odoo import fields, models, api


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    _description = 'Description'

    checklist_id = fields.Many2one(
        comodel_name='account.checklist',
        string='Checklist',
        required=False)

    steps = fields.Many2many('account.checklist.steps', string='Steps')

    steps_progress = fields.Float(compute='compute_steps_progress', string='Progress', store=True, recompute=True,
                                  default=0.0)

    # Compute the checklist steps progress
    @api.depends('steps')
    def compute_steps_progress(self):
        for record in self:
            total_len = self.env['account.checklist.steps'].search_count(
                [('checklist_id', '=', record.checklist_id.id)]) if record.checklist_id else 0
            steps_len = len(record.steps)
            if total_len != 0:
                record.steps_progress = (steps_len * 100) / total_len

    # On Change function that returns a domain for checklist_id
    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            serial_nb = self.equipment_id.serial_nb.id
            asset = self.env['account.asset'].search([('serial_nb', '=', serial_nb)])[0].id
            asset_checklists = self.env['account.asset.checklist'].search([('asset_id', '=', asset)])
            checklist_list = []
            if len(asset_checklists) > 0:
                for asset_checklist in asset_checklists:
                    checklist_list.append(asset_checklist.checklist_id.id)

            return {'domain': {'checklist_id': [('id', 'in', checklist_list)]}}

    # On Change function that returns a domain for steps
    @api.onchange('checklist_id')
    def onchange_checklist_id(self):
        if self.checklist_id:
            return {'domain': {'steps': [('checklist_id', '=', self.checklist_id.id)]}}

    # On Change function that change the last checklist infos in the account.asset.checklist
    @api.onchange('close_date')
    def onchange_close_date(self):
        if self.close_date:
            if self.checklist_id:
                serial_nb = self.equipment_id.serial_nb.id
                asset = self.env['account.asset'].search([('serial_nb', '=', serial_nb)])[0].id
                asset_checklist = self.env['account.asset.checklist'].search(
                    [('asset_id', '=', asset), ('checklist_id', '=', self.checklist_id.id)])[0]
                if asset_checklist:
                    if asset_checklist.next_date:
                        asset_checklist.last_date = self.close_date
                        asset_checklist.next_date = (
                                self.close_date + timedelta(days=asset_checklist.days)).strftime(
                            "%Y-%m-%d")
                        asset_checklist.days_check_state = 'done'

    # On change function that return a domain for user_id
    @api.onchange('maintenance_team_id')
    def onchange_maintenance_team_id(self):
        for record in self:
            if record.maintenance_team_id:
                members = self.env['maintenance.team'].browse(record.maintenance_team_id.id).member_ids.ids
                return {'domain': {'user_id': [('id', 'in', members)]}}

    # Compute the number of tasks related to the maintenance request
    tasks_count = fields.Integer(compute='compute_tasks_count')

    def compute_tasks_count(self):
        for record in self:
            record.tasks_count = self.env['project.task'].search_count(
                [('request_id', '=', self.id)])

    # Redirect to the field service model and list all tasks related to the maintenance request
    def get_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task',
            'view_mode': 'tree',
            'res_model': 'project.task',
            'domain': [('request_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Create asset related to the product
    def create_task(self):
        action_ctx = dict(self.env.context, default_request_id=self.id, default_equipment_id=self.equipment_id.id,
                          default_partner_id=self.equipment_id.res_partner_id.id,
                          default_name=(self.name + ' - ' + str(int(self.env['project.task'].search_count(
                              [('request_id', '=', self.id)])) + 1)),
                          default_project_id=self.env['project.project'].search([('is_fsm', '=', True)])[0].id)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'project.task',
            'view_id': self.env.ref('industry_fsm.project_task_view_form').id,
            'target': 'current',
            'context': action_ctx,
        }
