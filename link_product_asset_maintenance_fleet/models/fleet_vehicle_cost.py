from odoo import api, fields, models


class FleetVehicleCost(models.Model):
    _inherit = 'fleet.vehicle.cost'
    _description = 'Description'

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Service',
        required=False,
        domain=[('type', '=', 'service')])

    vendor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Vendor',
        required=False)

    quantity = fields.Float(
        string='Quantity',
        required=False,
        default=1)

    unit_cost = fields.Float(
        string='Unit Cost',
        required=False)

    # On Change function sets a default unit cost according to the vendor_id
    @api.onchange('vendor_id', 'product_id')
    def onchange_vendor_id(self):
        if self.vendor_id:
            if self.product_id:
                purchase_agreements = self.env['product.supplierinfo'].search(
                    [('product_tmpl_id', '=', self.product_id.id), ('name', '=', self.vendor_id.id)])
                if len(purchase_agreements) > 0:
                    purchase_agreement = purchase_agreements[0]
                    if purchase_agreement:
                        self.unit_cost = purchase_agreement.price if purchase_agreement.price else 0
                else:
                    self.unit_cost = 0

    # # On Change function sets a default unit cost according to the product_id
    # @api.onchange('product_id')
    # def onchange_product_id(self):
    #     if self.product_id:
    #         if self.vendor_id:
    #             purchase_agreements = self.env['product.supplierinfo'].search(
    #                 [('product_tmpl_id', '=', self.product_id.id), ('name', '=', self.vendor_id.id)])
    #             if len(purchase_agreements) > 0:
    #                 purchase_agreement = purchase_agreements[0]
    #                 if purchase_agreement:
    #                     self.unit_cost = purchase_agreement.price if purchase_agreement.price else 0
    #             else:
    #                 self.unit_cost = 0

    # On Change function that calculates the amount field when the quantity is changed
    @api.onchange('quantity')
    def onchange_quantity(self):
        if self.unit_cost > 0:
            self.amount = self.quantity * self.unit_cost

    # On Change function that calculates the amount field when the unit_cost is changed
    @api.onchange('unit_cost')
    def onchange_unit_cost(self):
        if self.quantity > 0:
            self.amount = self.quantity * self.unit_cost
