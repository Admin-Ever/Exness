from datetime import datetime, timedelta
from odoo import fields, models, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _description = 'Description'

    # asset_id = fields.Many2one(
    #     comodel_name='account.asset',
    #     string='Asset',
    #     required=False)

    # Compute the current driver of the vehicle
    driver_id = fields.Many2one(
        comodel_name='res.partner',
        string='Current Driver',
        readonly=True,
        compute='compute_current_driver',
        store=True)

    equipments_ids = fields.One2many(
        comodel_name='maintenance.equipment',
        inverse_name='fleet_vehicle_id',
        string='Equipments in the Vehicle',
        required=False)

    @api.depends('log_drivers.date_start', 'log_drivers.date_end', 'log_drivers.driver_id')
    def compute_current_driver(self):
        for record in self:
            drivers = self.env['fleet.vehicle.assignation.log'].search(
                [('vehicle_id', '=', record.id), ('date_start', '<=', datetime.now()), '|', ('date_end', '=', False),
                 ('date_end', '>=', datetime.now())])
            if len(drivers) > 0:
                current_driver = drivers[0]
                record.driver_id = current_driver.driver_id.id
            else:
                record.driver_id = False

    # Compute the number of accidents related to this vehicle
    accidents_count = fields.Integer(compute='compute_accidents_count')

    def compute_accidents_count(self):
        for record in self:
            record.accidents_count = self.env['fleet.accident'].search_count(
                [('vehicle_id', '=', self.id)])

    # Redirect to the accidents model and list all accidents related to the vehicle
    def get_accidents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Accident',
            'view_mode': 'tree,form',
            'res_model': 'fleet.accident',
            'domain': [('vehicle_id', '=', self.id)],
            'context': dict(self.env.context, default_vehicle_id=self.id, default_driver_id=
            self.env['fleet.vehicle.assignation.log'].search([('vehicle_id', '=', self.id), ('date_end', '=', False)])[
                0].driver_id.id if self.env['fleet.vehicle.assignation.log'].search(
                [('vehicle_id', '=', self.id), ('date_end', '=', False)]) else '')
        }

    # Compute the number of assets related to this vehicle
    assets_count = fields.Integer(compute='compute_assets_count')

    def compute_assets_count(self):
        for record in self:
            record.assets_count = self.env['account.asset'].search_count(
                [('vehicle_id', '=', self.id)])

    # Redirect to the assets model and list all assets related to the vehicle
    def get_assets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asset',
            'view_mode': 'tree,form',
            'res_model': 'account.asset',
            'domain': [('vehicle_id', '=', self.id)],
            'context': "{'create': False}"
        }

    # Create asset related to the vehicle
    def create_asset(self):
        action_ctx = dict(self.env.context, default_vehicle_id=self.id, default_asset_type='purchase',
                          default_name=(self.model_id.brand_id.name + '/' + self.model_id.name + (
                              (' - ' + self.vin_sn) if self.vin_sn else '')))

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.asset',
            'view_id': self.env.ref('account_asset.view_account_asset_form').id,
            'target': 'current',
            'context': action_ctx,
        }
