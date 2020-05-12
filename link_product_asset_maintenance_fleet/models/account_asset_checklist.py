from datetime import datetime, timedelta
from odoo import fields, models, api


class AccountAssetChecklist(models.Model):
    _name = 'account.asset.checklist'
    _description = 'Description'

    checklist_id = fields.Many2one(
        comodel_name='account.checklist',
        string='Checklist',
        required=True)

    odometer = fields.Float(
        string='Checklist frequency by Odometer',
        required=False)

    effective_odometer = fields.Float(
        string='Effective Odometer',
        required=False)

    last_odometer = fields.Float(
        string='Last Checklist by Odometer',
        required=False,
        readonly=True)

    next_odometer = fields.Float(
        string='Next Checklist by Odometer',
        required=False,
        readonly=True)

    odometer_check_state = fields.Selection(
        string='Checklist by Odometer State',
        selection=[('pending', 'Pending Service'),
                   ('done', 'Done Last Service'), ],
        required=False,
        readonly=True)

    days = fields.Float(
        string='Checklist frequency by Days',
        required=False)

    effective_date = fields.Date(
        string='Effective Date',
        required=False)

    last_date = fields.Date(
        string='Last Checklist by Date',
        required=False,
        readonly=True)

    next_date = fields.Date(
        string='Next Checklist by Date',
        required=False,
        readonly=True)

    days_check_state = fields.Selection(
        string='Checklist by Date State',
        selection=[('pending', 'Pending Service'),
                   ('done', 'Done Last Service'), ],
        required=False,
        readonly=True)

    asset_id = fields.Many2one(
        comodel_name='account.asset',
        string='Asset',
        required=False)

    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
        required=False)

    @api.model
    def create(self, vals):
        # Calculate next date
        if vals.get('days', '') != '' and vals.get('days', '') != 0.00:
            if vals.get('effective_date', '') != '':
                vals.update(
                    {'next_date': (datetime.strptime(vals.get('effective_date', ''), "%Y-%m-%d").date() + timedelta(days=vals.get('days', ''))).strftime("%Y-%m-%d")})
            elif vals.get('effective_date', '') == '':
                vals.update(
                    {'next_date': (datetime.now().date() + timedelta(days=vals.get('days', ''))).strftime(
                        "%Y-%m-%d")})
        elif vals.get('days', '') == '' and vals.get('days', '') == 0.00:
            vals.update({'next_date': False})

        # Calculate next odometer
        if vals.get('odometer', '') > 0:
            vehicle = self.env['fleet.vehicle'].browse(vals.get('vehicle_id', ''))
            if vals.get('effective_odometer', '') > 0:
                vals.update({'next_odometer': vals.get('effective_odometer', '') + vals.get('odometer', '')})
            elif vals.get('effective_odometer', '') == 0:
                vals.update({'next_odometer': vehicle.odometer + vals.get('odometer', '')})

        return super(AccountAssetChecklist, self).create(vals)
