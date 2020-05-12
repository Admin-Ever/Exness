from odoo import fields, models, api


class ResPartnerLicense(models.Model):
    _name = 'res.partner.license'
    _description = 'Description'

    res_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        required=False)

    name = fields.Char(
        string='File Name',
        required=True)

    file = fields.Binary(string="File", required=True)

    issue_date = fields.Date(
        string='Issue Date',
        required=False)

    expiry_date = fields.Date(
        string='Expiry Date',
        required=False)

    description = fields.Text(
        string="Description",
        required=False)
