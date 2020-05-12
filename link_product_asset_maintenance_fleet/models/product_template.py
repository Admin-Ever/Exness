from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Description'

    is_part = fields.Boolean(
        string='Is Part',
        required=False)

    product_templ = fields.Many2one(
        comodel_name='product.template',
        string='Parent Product',
        required=False,
        domain=[('is_part', '=', False)])

    model_no = fields.Char(
        string='Model No',
        required=False)

    product_condition = fields.Selection(
        string='Product Condition',
        selection=[('5', 'New'),
                   ('6', 'Used'),
                   ('7', 'Refurbished')],
        required=False, )

    vendor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Default Vendor',
        required=False)

    # Compute the number of assets related to the variants of this product
    assets_count = fields.Integer(compute='compute_assets_count')

    def compute_assets_count(self):
        for record in self:
            for rec in record.env['product.product'].search([('product_tmpl_id', '=', record.id)]):
                record.assets_count += rec.env['account.asset'].search_count(
                    [('product_prod', '=', rec.id)])

    # Compute the number of equipments related the variants of this product
    equipments_count = fields.Integer(compute='compute_equipments_count')

    def compute_equipments_count(self):
        for record in self:
            for rec in record.env['product.product'].search([('product_tmpl_id', '=', record.id)]):
                record.equipments_count += rec.env['maintenance.equipment'].search_count(
                    [('product_prod', '=', rec.id)])

    # Redirect to the assets model and list all assets related to the variants of this product
    def get_assets(self):
        for record in self:
            record.ensure_one()
            productprodid = record.env['product.product'].search([('product_tmpl_id', '=', record.id)])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Asset',
                'view_mode': 'tree,form',
                'res_model': 'account.asset',
                'domain': [('product_prod', 'in', productprodid.ids)],
                'context': "{'create': False}"
            }

    # Redirect to the equipments model and list all equipments related to the variants of this product
    def get_equipments(self):
        for record in self:
            record.ensure_one()
            productprodid = record.env['product.product'].search([('product_tmpl_id', '=', record.id)])
            return {
                'type': 'ir.actions.act_window',
                'name': 'Equipment',
                'view_mode': 'tree,form',
                'res_model': 'maintenance.equipment',
                'domain': [('product_prod', 'in', productprodid.ids)],
                'context': "{'create': False}"
            }

    # Create asset related to the variants of this product
    def create_asset(self):
        action_ctx = dict(self.env.context, default_product_templ=self.id, default_asset_type='purchase')

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.asset',
            'view_id': self.env.ref('account_asset.view_account_asset_form').id,
            'target': 'current',
            'context': action_ctx,
        }

    # Create equipment related to the variants of this product
    def create_equipment(self):
        action_ctx = dict(self.env.context, default_product_templ=self.id)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'maintenance.equipment',
            'view_id': self.env.ref('maintenance.hr_equipment_view_form').id,
            'target': 'current',
            'context': action_ctx,
        }
