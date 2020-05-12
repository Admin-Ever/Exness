from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Description'

    # Compute the number of assets related to this product
    assets_count = fields.Integer(compute='compute_assets_count')

    def compute_assets_count(self):
        for record in self:
            record.assets_count = self.env['account.asset'].search_count(
                [('product_prod', '=', self.id)])

    # Compute the number of equipments related to this product
    equipments_count = fields.Integer(compute='compute_equipments_count')

    def compute_equipments_count(self):
        for record in self:
            record.equipments_count = self.env['maintenance.equipment'].search_count(
                [('product_prod', '=', self.id)])

    # Redirect to the assets model and list all assets related to the product
    def get_assets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Asset',
            'view_mode': 'tree,form',
            'res_model': 'account.asset',
            'domain': [('product_prod', '=', self.id)],
            'context': "{'create': False}"
        }

    # Redirect to the equipments model and list all equipments related to the product
    def get_equipments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Equipment',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.equipment',
            'domain': [('product_prod', '=', self.id)],
            'context': "{'create': False}"
        }

    # Create asset related to the product
    def create_asset(self):
        action_ctx = dict(self.env.context, default_product_templ=self.product_tmpl_id.id, default_product_prod=self.id,
                          default_asset_type='purchase')

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.asset',
            'view_id': self.env.ref('account_asset.view_account_asset_form').id,
            'target': 'current',
            'context': action_ctx,
        }

    # Create equipment related to the product
    def create_equipment(self):
        action_ctx = dict(self.env.context, default_product_templ=self.product_tmpl_id.id, default_product_prod=self.id)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'maintenance.equipment',
            'view_id': self.env.ref('maintenance.hr_equipment_view_form').id,
            'target': 'current',
            'context': action_ctx,
        }
