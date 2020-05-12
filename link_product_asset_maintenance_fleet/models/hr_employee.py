from odoo import fields, models, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Description'

    # Calculating the total number of equipments assigned to this employee
    equipments_count = fields.Integer('Equipments', compute='_compute_equipments_count')

    def _compute_equipments_count(self):
        for employee in self:
            eq_count = len(employee.equipment_ids)
            cars = self.env['fleet.vehicle.assignation.log'].search([
                ('driver_id', 'in', self.user_id.partner_id.ids)]).mapped('vehicle_id')
            if len(cars) > 0:
                cars_equipments = self.env['maintenance.equipment'].search([
                    ('fleet_vehicle_id', 'in', cars.ids)])
                if len(cars_equipments) > 0:
                    eq_count = eq_count + len(cars_equipments)

            employee.equipments_count = eq_count

    # Redirect to the equipments model and list all equipments related to the employee
    def get_equipments(self):
        self.ensure_one()
        # cars_equipments = None
        cars = self.env['fleet.vehicle.assignation.log'].search([
            ('driver_id', 'in', self.user_id.partner_id.ids)]).mapped('vehicle_id')
        if len(cars) > 0:
            cars_equipments = self.env['maintenance.equipment'].search([
                ('fleet_vehicle_id', 'in', cars.ids)]).ids
            if len(cars_equipments) > 0:
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Equipment',
                    'view_mode': 'tree,form',
                    'res_model': 'maintenance.equipment',
                    'domain': ['|', ('employee_id', '=', self.id), ('id', 'in', cars_equipments)],
                    'context': "{'create': False}"
                }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Equipment',
                'view_mode': 'tree,form',
                'res_model': 'maintenance.equipment',
                'domain': [('employee_id', '=', self.id)],
                'context': "{'create': False}"
            }
