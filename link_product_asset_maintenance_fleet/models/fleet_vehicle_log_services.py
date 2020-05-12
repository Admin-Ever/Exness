from datetime import datetime, timedelta
from odoo import fields, models, api


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _description = 'Description'

    accident_id = fields.Many2one(
        comodel_name='fleet.accident',
        string='Accident',
        required=False)

    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('pending', 'In Progress'),
                   ('done', 'Done')],
        readonly=True,
        default='draft')

    total_indicative = fields.Float(
        string='Indicative calculated cost',
        required=False,
        readonly=True)

    close_date = fields.Date(
        string='Closed Date',
        required=False)

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
    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        if self.vehicle_id:
            asset_checklists = self.env['account.asset.checklist'].search([('vehicle_id', '=', self.vehicle_id.id)])
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

    # On Change function that returns a value for total_indicative
    @api.onchange('cost_ids')
    def onchange_cost_ids(self):
        tot_sum = 0
        for line in self.cost_ids:
            tot_sum = tot_sum + line.amount
        self.total_indicative = tot_sum

    # On Change function that change vendor_id in cost_ids one2many
    @api.onchange('vendor_id')
    def onchange_vendor_id(self):
        for line in self.cost_ids:
            line.vendor_id = self.vendor_id.id
            if line.product_id:
                purchase_agreements = self.env['product.supplierinfo'].search(
                    [('product_tmpl_id', '=', line.product_id.id), ('name', '=', line.vendor_id.id)])
                if len(purchase_agreements) > 0:
                    purchase_agreement = purchase_agreements[0]
                    if purchase_agreement:
                        line.unit_cost = purchase_agreement.price if purchase_agreement.price else 0
                else:
                    line.unit_cost = 0

    # On Change function that change the last checklist infos in the account.asset.checklist
    @api.onchange('close_date')
    def onchange_close_date(self):
        if self.close_date:
            if self.checklist_id:
                asset_checklist = self.env['account.asset.checklist'].search(
                    [('vehicle_id', '=', self.vehicle_id.id), ('checklist_id', '=', self.checklist_id.id)])[0]
                if asset_checklist:
                    if asset_checklist.next_date:
                        asset_checklist.last_date = self.close_date
                        asset_checklist.next_date = (self.close_date + timedelta(days=asset_checklist.days)).strftime(
                            "%Y-%m-%d")
                        asset_checklist.days_check_state = 'done'
                    if asset_checklist.next_odometer > 0:
                        asset_checklist.last_odometer = self.odometer
                        asset_checklist.next_odometer = self.odometer + asset_checklist.odometer
                        asset_checklist.odometer_check_state = 'done'


# Change the state of the service log to Pending
def change_pending(self):
    for record in self:
        record.state = 'pending'


# Change the state of the service log to Done
def change_done(self):
    for record in self:
        record.state = 'done'
        record.close_date = datetime.now().date()
