from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    _description = 'Description'

    product_templ = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=False)

    product_prod = fields.Many2one(
        comodel_name='product.product',
        string='Product Variant',
        required=False)

    barcode = fields.Char(
        string='Product Barcode',
        related='product_prod.barcode',
        readonly=True,
        store=True)

    serial_nb = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Serial Number',
        required=False)

    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
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

    # On change function that return a domain for the serial_nb many2one and get the product barcode
    @api.onchange('product_prod')
    def onchange_product_prod(self):
        for record in self:
            return {'domain': {'serial_nb': [('product_id', '=', record.product_prod.id)]}}

    # On change function that sets asset name according to the serial_nb
    @api.onchange('serial_nb')
    def onchange_serial_nb(self):
        for record in self:
            if not record.vehicle_id:
                record.name = ((record.product_prod.name if record.product_prod.name else '') + ' - ' + (
                    record.serial_nb.name if record.serial_nb.name else '')) if record.serial_nb else ''

    # # Compute the number of equipments related the asset
    # equipments_count = fields.Integer(compute='compute_equipments_count')
    #
    # def compute_equipments_count(self):
    #     for record in self:
    #         record.equipments_count = self.env['maintenance.equipment'].search_count(
    #             [('asset_id', '=', self.id)])

    # # Compute the number of vehicles related to the asset
    # vehicles_count = fields.Integer(compute='compute_vehicles_count')
    #
    # def compute_vehicles_count(self):
    #     for record in self:
    #         record.vehicles_count = self.env['fleet.vehicle'].search_count(
    #             [('asset_id', '=', self.id)])

    # # Redirect to the equipments model and list all equipments related to the asset
    # def get_equipment(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Equipment',
    #         'view_mode': 'tree',
    #         'res_model': 'maintenance.equipment',
    #         'domain': [('asset_id', '=', self.id)],
    #         'context': "{'create': False}"
    #     }

    # # Redirect to the vehicles model and list all vehicles related to the asset
    # def get_vehicle(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Asset',
    #         'view_mode': 'tree',
    #         'res_model': 'fleet.vehicle',
    #         'domain': [('asset_id', '=', self.id)],
    #         'context': "{'create': False}"
    #     }

    # # Create equipment related to the asset
    # def create_equipment(self):
    #     action_ctx = dict(self.env.context, default_product_prod=(self.product_prod.id if self.product_prod else ''),
    #                       default_serial_nb=(self.serial_nb.id if self.serial_nb else ''),
    #                       default_asset_id=self.id)
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'maintenance.equipment',
    #         'view_id': self.env.ref('maintenance.hr_equipment_view_form').id,
    #         'target': 'current',
    #         'context': action_ctx,
    #     }

    # # Create vehicle related to the asset
    # def create_vehicle(self):
    #     action_ctx = dict(self.env.context, default_asset_id=self.id)
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'fleet.vehicle',
    #         'view_id': self.env.ref('fleet.fleet_vehicle_view_form').id,
    #         'target': 'current',
    #         'context': action_ctx,
    #     }

    # Compute the number of checklists related to this asset
    checklists_count = fields.Integer(compute='compute_checklists_count')

    def compute_checklists_count(self):
        for record in self:
            record.checklists_count = self.env['account.asset.checklist'].search_count(
                [('asset_id', '=', self.id)])

    # Redirect to the assets model and list all assets related to the product
    def get_checklists(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Checklists',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.checklist',
            'domain': [('asset_id', '=', self.id)],
            'context': dict(self.env.context, default_asset_id=self.id, default_vehicle_id=self.vehicle_id.id)
        }

    # Constraint for not creating more than 1 asset with the same serial_nb
    @api.constrains('serial_nb')
    def check_serial_nb(self):
        for record in self:
            if record.serial_nb:
                serial_nb_asset = self.env['account.asset'].search(
                    [('serial_nb', '=', record.serial_nb.id), ('id', '!=', record.id)])
                if len(serial_nb_asset) > 0:
                    raise ValidationError(_('There is already an Asset with the same Serial Number'))

    # Overriding the create function to change is_asset in stock.production.lot
    @api.model
    def create(self, vals):
        if vals.get('serial_nb', '') != '':
            lot = self.env['stock.production.lot'].browse(vals.get('serial_nb', ''))
            lot.is_asset = True
        return super(AccountAsset, self).create(vals)

    # Overriding the write function to change is_asset in stock.production.lot
    def write(self, vals):
        if vals.get('serial_nb', '') != self.serial_nb:
            if self.serial_nb != '':
                old_lot = self.env['stock.production.lot'].browse(self.serial_nb.id)
                old_lot.is_asset = False
            if vals.get('serial_nb', '') != '':
                new_lot = self.env['stock.production.lot'].browse(vals.get('serial_nb', ''))
                new_lot.is_asset = True
        return super(AccountAsset, self).write(vals)

    # Overriding the unlink function to change is_asset in stock.production.lot
    def unlink(self):
        for record in self:
            if record.serial_nb:
                lot = self.env['stock.production.lot'].browse(record.serial_nb.id)
                lot.is_asset = False
        return super(AccountAsset, self).unlink()

    # Scheduled action for the Assets Checklist
    @api.model
    def asset_checklist_cron(self):
        today = datetime.now().date()
        assets = self.env['account.asset'].search([('active', '=', True)])
        for asset in assets:
            asset_checklists = asset.env['account.asset.checklist'].search([('asset_id', '=', asset.id)])
            for asset_checklist in asset_checklists:
                # if the asset is related to a vehicle
                if asset.vehicle_id:
                    # if the asset checklist is based on days
                    if asset_checklist.next_date:
                        # if the asset checklist is done before
                        if asset_checklist.last_date:
                            # if we've passed the date of the last check
                            if today > asset_checklist.last_date:
                                # check if there is not a previous service not done
                                if asset_checklist.days_check_state == 'done':
                                    self.env['fleet.vehicle.log.services'].create({
                                        'vehicle_id': asset_checklist.vehicle_id.id,
                                        'date': asset_checklist.next_date,
                                        'checklist_id': asset_checklist.checklist_id.id,
                                        'state': 'draft'
                                    })
                                    asset_checklist.days_check_state = 'pending'
                        # if the asset checklist is never done before
                        elif not asset_checklist.last_date:
                            # check if there is not a previous service not done
                            if not asset_checklist.days_check_state:
                                self.env['fleet.vehicle.log.services'].create({
                                    'vehicle_id': asset_checklist.vehicle_id.id,
                                    'date': asset_checklist.next_date,
                                    'checklist_id': asset_checklist.checklist_id.id,
                                    'state': 'draft'
                                })
                            asset_checklist.days_check_state = 'pending'

                    # if the asset checklist is based on odometer
                    if asset_checklist.next_odometer > 0:
                        # if the vehicle odometer is bigger than the next service odometer
                        if asset_checklist.vehicle_id.odometer >= asset_checklist.next_odometer:
                            # check if there is not a previous service not done
                            if asset_checklist.odometer_check_state != 'pending':
                                self.env['fleet.vehicle.log.services'].create({
                                    'vehicle_id': asset_checklist.vehicle_id.id,
                                    'date': today,
                                    'checklist_id': asset_checklist.checklist_id.id,
                                    'odometer': asset_checklist.vehicle_id.odometer,
                                    'state': 'draft'
                                })

                # if the asset is not related to a vehicle
                elif not asset.vehicle_id:
                    # if the asset checklist is based on days
                    if asset_checklist.next_date:
                        # if the asset checklist is done before
                        if asset_checklist.last_date:
                            # if we've passed the date of the last check
                            if today > asset_checklist.last_date:
                                # check if there is not a previous maintenance not done
                                if asset_checklist.days_check_state == 'done':
                                    self.env['maintenance.request'].create({
                                        'name': asset_checklist.checklist_id.name + ' Checklist - ' + asset_checklist.next_date,
                                        'equipment_id': self.env['maintenance.equipment'].search(
                                            [('serial_nb', '=', asset.serial_nb)])[0].id,
                                        'maintenance_type': 'preventive',
                                        'schedule_date': datetime.combine(asset_checklist.next_date,
                                                                          datetime.min.time()),
                                        'checklist_id': asset_checklist.checklist_id.id,
                                    })
                                    asset_checklist.days_check_state = 'pending'
                        # if the asset checklist is never done before
                        elif not asset_checklist.last_date:
                            # check if there is not a previous maintenance not done
                            if not asset_checklist.days_check_state:
                                self.env['maintenance.request'].create({
                                    'name': asset_checklist.checklist_id.name + ' Checklist - ' + asset_checklist.next_date,
                                    'equipment_id': self.env['maintenance.equipment'].search(
                                        [('serial_nb', '=', asset.serial_nb)])[0].id,
                                    'maintenance_type': 'preventive',
                                    'schedule_date': datetime.combine(asset_checklist.next_date,
                                                                      datetime.min.time()),
                                    'checklist_id': asset_checklist.checklist_id.id,
                                })
                                asset_checklist.days_check_state = 'pending'
