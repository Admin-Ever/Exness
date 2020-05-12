from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'
    _description = 'Description'

    usage = fields.Selection(selection_add=[('employee', 'Employee Location'), ('department', 'Department Location'),
                                            ('vehicle', 'Vehicle Location')])

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        required=False)

    hr_department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        required=False)

    fleet_vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
        required=False)

    # On change function that resets res_partner_id and hr_department_id
    @api.onchange('usage')
    def onchange_usage(self):
        for record in self:
            record.res_partner_id = False
            record.hr_department_id = False
            record.fleet_vehicle_id = False

    # On change function that sets location name
    @api.onchange('res_partner_id')
    def onchange_res_partner_id(self):
        for record in self:
            if record.usage != '':
                if record.usage == 'customer':
                    name = 'Customer Location'
                elif record.usage == 'supplier':
                    name = 'Vendor Location'
                elif record.usage == 'employee':
                    name = 'Employee Location'
                record.name = ((name if name else '') + ' - ' + (
                    record.res_partner_id.name if record.res_partner_id.name else '')) if record.res_partner_id else ''

    # On change function that sets location name
    @api.onchange('hr_department_id')
    def onchange_hr_department_id(self):
        for record in self:
            if record.usage != '':
                if record.usage == 'department':
                    record.name = ('Department Location - ' + (
                        record.hr_department_id.name if record.hr_department_id.name else '')) if record.hr_department_id else ''

    # On change function that sets location name
    @api.onchange('fleet_vehicle_id')
    def onchange_fleet_vehicle_id(self):
        for record in self:
            if record.usage != '':
                if record.usage == 'vehicle':
                    record.name = ('Vehicle Location - ' + (
                            record.fleet_vehicle_id.model_id.name + '/' + record.fleet_vehicle_id.vin_sn)) if record.fleet_vehicle_id else ''

    @api.model
    def create(self, vals):
        result = super(StockLocation, self).create(vals)
        if vals.get('res_partner_id', '') != '':
            partner = self.env['res.partner'].browse(vals.get('res_partner_id', ''))
            if vals.get('usage', '') == 'customer':
                partner.property_stock_customer = result.id
            elif vals.get('usage', '') == 'supplier':
                partner.property_stock_supplier = result.id
            elif vals.get('usage', '') == 'employee':
                partner.property_stock_customer = result.id
        return result

    def write(self, vals):
        result = super(StockLocation, self).write(vals)
        if vals.get('res_partner_id', '') != '':
            partner = self.env['res.partner'].browse(vals.get('res_partner_id', ''))
            if vals.get('usage', '') == 'customer':
                partner.property_stock_customer = self.id
            elif vals.get('usage', '') == 'supplier':
                partner.property_stock_supplier = self.id
            elif vals.get('usage', '') == 'employee':
                partner.property_stock_customer = self.id
        return result
