from odoo import fields, models, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    _description = 'Description'
    
    is_asset = fields.Boolean(
        string='Asset',
        required=False,
        readonly=True)

    is_equipment = fields.Boolean(
        string='Equipment',
        required=False,
        readonly=True)

    # Compute the current location of the LOT / SN
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Current Location',
        required=False,
        readonly=True,
        compute='compute_current_location')

    def compute_current_location(self):
        for record in self:
            quantity = self.env['stock.quant'].search([('quantity', '>', 0), ('lot_id', '=', record.id)])
            if len(quantity) > 0:
                current_quantity = quantity[0]
                record.location_id = self.env['stock.location'].browse(current_quantity.location_id.id)

    # Redirect to the assets model and list all assets related to the lot / serial number
    def get_assets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asset',
            'view_mode': 'tree',
            'res_model': 'account.asset',
            'domain': [('serial_nb', '=', self.id)],
            'context': "{'create': False}"
        }

    # Redirect to the equipments model and list all equipments related to the lot / serial number
    def get_equipments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asset',
            'view_mode': 'tree',
            'res_model': 'maintenance.equipment',
            'domain': [('serial_nb', '=', self.id)],
            'context': "{'create': False}"
        }
