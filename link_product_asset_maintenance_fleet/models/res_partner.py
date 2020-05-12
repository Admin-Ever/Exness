from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Description'

    code = fields.Char(
        string='Code',
        required=False)

    is_customer = fields.Boolean(
        string='Customer',
        required=False)

    is_supplier = fields.Boolean(
        string='Supplier',
        required=False)

    is_partner = fields.Boolean(
        string='Partner',
        required=False)

    is_interested_person = fields.Boolean(
        string='Interested Person',
        required=False)

    is_driver = fields.Boolean(
        string='Driver',
        required=False)

    telefax = fields.Char(
        string='Telefax',
        required=False)

    common_discount = fields.Float(
        string='Common Discount',
        required=False)

    credit_limit_date = fields.Date(
        string='Credit Limit Date',
        required=False)

    accidents_ids = fields.One2many(
        comodel_name='fleet.accident',
        inverse_name='driver_id',
        string='Accidents',
        required=False)

    licenses_ids = fields.One2many(
        comodel_name='res.partner.license',
        inverse_name='res_partner_id',
        string='Licenses',
        required=False)

    deletion_mark = fields.Boolean(
        string='Deletion Mark',
        required=False)

    is_locked = fields.Boolean(
        string='Locked',
        required=False)

    is_master_account = fields.Boolean(
        string='Master Account',
        required=False)

    overdue_days = fields.Float(
        string='Overdue Days',
        required=False)

    invoice_method = fields.Selection(
        string='Default Invoicing Method',
        selection=[('cash', 'Cash'),
                   ('credit', 'Credit'),
                   ('mixed', 'Mixed')],
        required=False, )

    payment_by = fields.Many2one(
        comodel_name='account.journal',
        string='Payment By',
        required=False)

    # Overriding the create function to check if customer or supplier
    @api.model
    def create(self, vals):
        if 'is_supplier' in vals:
            if vals['is_supplier']:
                vals['supplier_rank'] = 1
            else:
                vals['supplier_rank'] = 0
        if 'is_customer' in vals:
            if vals['is_customer']:
                vals['customer_rank'] = 1
            else:
                vals['customer_rank'] = 0

        return super(ResPartner, self).create(vals)
