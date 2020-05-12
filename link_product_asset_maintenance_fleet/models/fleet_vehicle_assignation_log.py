from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, _


class FleetVehicleAssignationLog(models.Model):
    _inherit = 'fleet.vehicle.assignation.log'
    _description = 'Description'

    date_start = fields.Datetime(
        string='Start Date',
        required=True)

    date_end = fields.Datetime(
        string='End Date',
        required=False)

    description_start = fields.Text(
        string="Start Description",
        required=False)

    description_end = fields.Text(
        string="End Description",
        required=False)

    start_sign = fields.Char(
        string='Start Signature',
        required=False)

    end_sign = fields.Char(
        string='End Signature',
        required=False)

    # Constraint for checking if date_end is after date_start
    @api.constrains('date_end')
    def check_serial_nb(self):
        for record in self:
            if record.date_end:
                if record.date_end <= record.date_start:
                    raise ValidationError(_('End Date must be after Start Date'))

    # Constraint for checking if date_start is before date_end
    @api.constrains('date_start')
    def check_serial_nb(self):
        for record in self:
            if record.date_end:
                if record.date_start >= record.date_end:
                    raise ValidationError(_('End Date must be after Start Date'))

    @api.model
    def create(self, vals):
        drivers_not_ended = self.env['fleet.vehicle.assignation.log'].search(
            [('vehicle_id', '=', vals.get('vehicle_id', '')), ('date_end', '=', False)])
        for driver_not_ended in drivers_not_ended:
            driver_not_ended.date_end = datetime.now()

        return super(FleetVehicleAssignationLog, self).create(vals)
