from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    _description = 'Description'

    equipment_assign_to = fields.Selection(selection_add=[('contact', 'Contact'), ('vehicle', 'Vehicle')])

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        required=False)

    fleet_vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
        required=False)

    product_templ = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=False)

    product_prod = fields.Many2one(
        comodel_name='product.product',
        string='Product Variant',
        required=False)

    # asset_id = fields.Many2one(
    #     comodel_name='account.asset',
    #     string='Asset',
    #     required=False)

    serial_nb = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Serial Number',
        required=False)

    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Current Location',
        required=False,
        related='serial_nb.location_id',
        readonly=True)

    # On change function that return a domain for the product_prod many2one
    @api.onchange('product_templ')
    def onchange_product_templ(self):
        for record in self:
            return {'domain': {'product_prod': [('product_tmpl_id', '=', record.product_templ.id)]}}

    # On change function that return a domain for the serial_nb many2one
    @api.onchange('product_prod')
    def onchange_product_prod(self):
        for record in self:
            return {'domain': {'serial_nb': [('product_id', '=', record.product_prod.id)]}}

    # On change function that sets equipment name and sets res_partner_id according to the serial_nb
    @api.onchange('serial_nb')
    def onchange_serial_nb(self):
        for record in self:
            record.name = ((record.product_prod.name if record.product_prod.name else '') + ' - ' + (
                record.serial_nb.name if record.serial_nb.name else '')) if record.serial_nb else ''

            # if record.equipment_assign_to == 'contact':
            #     stock_quantity = record.env['stock.quant'].search(
            #         [('lot_id', '=', record.serial_nb.id), ('inventory_quantity', '>', 0)])
            #     if stock_quantity.location_id.res_partner_id:
            #         respartner = stock_quantity.location_id.res_partner_id if stock_quantity.location_id.res_partner_id else None
            #         record.res_partner_id = respartner.id if respartner else ''
            # else:
            #     record.res_partner_id = ''

    # On change function that sets res_partner_id and fleet_vehicle_id according to the equipment_assign_to
    @api.onchange('equipment_assign_to')
    def onchange_equipment_assign_to(self):
        for record in self:
            if record.equipment_assign_to == 'contact':
                stock_quantity = record.env['stock.quant'].search(
                    [('lot_id', '=', record.serial_nb.id), ('inventory_quantity', '>', 0)])
                if stock_quantity.location_id.res_partner_id:
                    respartner = stock_quantity.location_id.res_partner_id if stock_quantity.location_id.res_partner_id else None
                    record.res_partner_id = respartner.id if respartner else ''
            elif record.equipment_assign_to == 'vehicle':
                stock_quantity = record.env['stock.quant'].search(
                    [('lot_id', '=', record.serial_nb.id), ('inventory_quantity', '>', 0)])
                if stock_quantity.location_id.res_partner_id:
                    fleetvehicle = stock_quantity.location_id.fleet_vehicle_id if stock_quantity.location_id.fleet_vehicle_id else None
                    record.fleet_vehicle_id = fleetvehicle.id if fleetvehicle else ''
            elif record.equipment_assign_to == 'other':
                record.location = 'Other'
            else:
                record.location = ''

    # On change function that sets location same as employee
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for record in self:
            if record.employee_id:
                record.location = record.employee_id.name

    # On change function that sets location same as department
    @api.onchange('department_id')
    def onchange_department_id(self):
        for record in self:
            if record.department_id:
                record.location = record.department_id.name

    # On change function that sets location same as contact
    @api.onchange('res_partner_id')
    def onchange_res_partner_id(self):
        for record in self:
            if record.res_partner_id:
                record.location = record.res_partner_id.name

    # On change function that sets location same as vehicle
    @api.onchange('fleet_vehicle_id')
    def onchange_fleet_vehicle_id(self):
        for record in self:
            if record.fleet_vehicle_id:
                record.location = record.fleet_vehicle_id.model_id.name + '/' + record.fleet_vehicle_id.vin_sn

    # On change function that return a domain for technician_user_id
    @api.onchange('maintenance_team_id')
    def onchange_maintenance_team_id(self):
        for record in self:
            if record.maintenance_team_id:
                members = self.env['maintenance.team'].browse(record.maintenance_team_id.id).member_ids.ids
                return {'domain': {'technician_user_id': [('id', 'in', members)]}}

    # Constraint for not creating more than 1 equipment with the same serial_nb
    @api.constrains('serial_nb')
    def check_serial_nb(self):
        for record in self:
            if record.serial_nb:
                serial_nb_equipment = self.env['maintenance.equipment'].search(
                    [('serial_nb', '=', record.serial_nb.id), ('id', '!=', record.id)])
                if len(serial_nb_equipment) > 0:
                    raise ValidationError(_('There is already an Equipment with the same Serial Number'))

    # Overriding the create function to change is_equipment in stock.production.lot
    @api.model
    def create(self, vals):
        if vals.get('serial_nb', '') != '':
            lot = self.env['stock.production.lot'].browse(vals.get('serial_nb', ''))
            lot.is_equipment = True
        return super(MaintenanceEquipment, self).create(vals)

    # Overriding the write function to change is_equipment in stock.production.lot
    def write(self, vals):
        if vals.get('serial_nb', '') != self.serial_nb:
            if self.serial_nb != '':
                old_lot = self.env['stock.production.lot'].browse(self.serial_nb.id)
                old_lot.is_equipment = False
            if vals.get('serial_nb', '') != '':
                new_lot = self.env['stock.production.lot'].browse(vals.get('serial_nb', ''))
                new_lot.is_equipment = True
        return super(MaintenanceEquipment, self).write(vals)

    # Overriding the unlink function to change is_equipment in stock.production.lot
    def unlink(self):
        for record in self:
            if record.serial_nb:
                lot = self.env['stock.production.lot'].browse(record.serial_nb.id)
                lot.is_equipment = False
        return super(MaintenanceEquipment, self).unlink()
