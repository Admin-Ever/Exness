from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Overriding the validate method to make changes in the equipments related to the serial numbers
    def button_validate(self):
        for record in self:
            for line in record.move_line_ids_without_package:
                equipments = self.env['maintenance.equipment'].search(
                    [('serial_nb', '=', line.lot_id.id), ('product_prod', '=', line.product_id.id)])
                # Check if there is equipments with the serial numbers chosen
                if len(equipments) > 0:
                    equipment = equipments[0]
                    location = record.partner_id.property_stock_customer
                    location_destination = record.location_dest_id

                    # If the destination location is a customer or vendor location
                    if location.usage == 'customer' or location.usage == 'vendor':
                        equipment.equipment_assign_to = 'contact'
                        equipment.res_partner_id = location.res_partner_id.id
                        equipment.department_id = False
                        equipment.employee_id = False
                        equipment.fleet_vehicle_id = False

                    # If the destination location is an employee location
                    elif location.usage == 'employee':
                        users = self.env['res.users'].search([('partner_id', '=', location.res_partner_id.id)])
                        if len(users) > 0:
                            user = users[0]
                            employees = self.env['hr.employee'].search(
                                [('user_id', '=', user.id)])
                            if len(employees) > 0:
                                employee = employees[0]
                                equipment.equipment_assign_to = 'employee'
                                equipment.employee_id = employee.id
                                equipment.department_id = False
                                equipment.res_partner_id = False
                                equipment.fleet_vehicle_id = False

                    # If the destination location is a department location
                    if location_destination.usage == 'department':
                        equipment.equipment_assign_to = 'department'
                        equipment.department_id = location_destination.hr_department_id.id
                        equipment.res_partner_id = False
                        equipment.employee_id = False
                        equipment.fleet_vehicle_id = False

                    # If the destination location is a vehicle location
                    elif location_destination.usage == 'vehicle':
                        equipment.equipment_assign_to = 'vehicle'
                        equipment.fleet_vehicle_id = location_destination.fleet_vehicle_id.id
                        equipment.res_partner_id = False
                        equipment.department_id = False
                        equipment.employee_id = False

        return super(StockPicking, self).button_validate()
