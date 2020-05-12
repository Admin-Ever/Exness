from odoo import fields, models, api


class FleetAccident(models.Model):
    _name = 'fleet.accident'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Description'

    def name_get(self):
        result = []
        for record in self:
            result.append((record.accident_date, record.vehicle_id.model_id.name))
        return result

    vehicle_id = fields.Many2one(
        comodel_name='fleet.vehicle',
        string='Vehicle',
        required=True)

    accident_date = fields.Date(
        string='Accident Date',
        required=True)

    driver_id = fields.Many2one(
        comodel_name='res.partner',
        string='Driver',
        required=False)

    insurance = fields.Char(
        string='Insurance Info',
        required=False)

    second_party_name = fields.Char(
        string='Second party name',
        required=False)

    second_party_phone = fields.Char(
        string='Second party phone',
        required=False)

    second_party_insurance = fields.Char(
        string='Second party insurance Info',
        required=False)

    # street = fields.Char()
    # street2 = fields.Char()
    # zip = fields.Char(change_default=True)
    # city = fields.Char()
    # state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
    #                            domain="[('country_id', '=?', country_id)]")
    # country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    latitude = fields.Float(
        string='Latitude',
        required=False)

    longitude = fields.Float(
        string='Longitude',
        required=False)

    # Compute the number of services related to this accident
    services_count = fields.Integer(compute='compute_services_count')

    def compute_services_count(self):
        for record in self:
            record.services_count = self.env['fleet.vehicle.log.services'].search_count(
                [('accident_id', '=', self.id)])

    # Redirect to the services model and list all services related to the accident
    def get_services(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service',
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle.log.services',
            'domain': [('accident_id', '=', self.id)],
            'context': dict(self.env.context, default_accident_id=self.id, default_vehicle_id=self.vehicle_id.id)
        }

    # On Change function that resets the value of state_id when country_id is changed
    @api.onchange('country_id')
    def onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    # On Change function that sets country_id according the the chosen state_id
    @api.onchange('state_id')
    def onchange_state_id(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    # # Function that redirects to google maps with the address from the fields
    # def open_map(self):
    #     for record in self:
    #         url = "http://maps.google.com/maps?oi=map&q="
    #         if record.street:
    #             url += record.street.replace(' ', '+')
    #         if record.street2:
    #             url += '+' + record.street2.replace(' ', '+')
    #         if record.city:
    #             url += '+'+record.city.replace(' ', '+')
    #         if record.state_id:
    #             url += '+'+record.state_id.name.replace(' ', '+')
    #         if record.country_id:
    #             url += '+'+record.country_id.name.replace(' ', '+')
    #         if record.zip:
    #             url += '+'+record.zip.replace(' ', '+')
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'target': 'new',
    #         'url': url
    #     }

    # Function that redirects to google maps with the address from the fields
    def open_map(self):
        for record in self:
            url = "https://www.google.com/maps/search/?api=1&query="
            if record.latitude:
                url += str(record.latitude)
            if record.longitude:
                url += ',' + str(record.longitude)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url
        }
