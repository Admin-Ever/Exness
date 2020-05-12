# -*- coding: utf-8 -*-
# from odoo import http


# class LinkProductAssetMaintenanceFleet(http.Controller):
#     @http.route('/link_product_asset_maintenance_fleet/link_product_asset_maintenance_fleet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/link_product_asset_maintenance_fleet/link_product_asset_maintenance_fleet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('link_product_asset_maintenance_fleet.listing', {
#             'root': '/link_product_asset_maintenance_fleet/link_product_asset_maintenance_fleet',
#             'objects': http.request.env['link_product_asset_maintenance_fleet.link_product_asset_maintenance_fleet'].search([]),
#         })

#     @http.route('/link_product_asset_maintenance_fleet/link_product_asset_maintenance_fleet/objects/<model("link_product_asset_maintenance_fleet.link_product_asset_maintenance_fleet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('link_product_asset_maintenance_fleet.object', {
#             'object': obj
#         })
