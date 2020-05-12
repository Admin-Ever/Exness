# -*- coding: utf-8 -*-
{
    'name': "Link Product Asset Maintenance Fleet",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ever Business Solutions",
    'website': "http://www.ever-bs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account', 'account_asset', 'hr_maintenance', 'fleet', 'industry_fsm', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/product_product.xml',
        'views/account_asset.xml',
        'views/maintenance_equipment.xml',
        'views/product_template.xml',
        'views/fleet_vehicle.xml',
        'views/stock_location.xml',
        'views/maintenance_request.xml',
        'views/project_task.xml',
        'views/fleet_vehicle_assignation_log.xml',
        'views/fleet_accident.xml',
        'views/res_partner.xml',
        'views/fleet_vehicle_log_services.xml',
        'views/fleet_vehicle_log_contract.xml',
        'views/account_checklist.xml',
        'views/account_asset_checklist.xml',
        'views/stock_production_lot.xml',
        'views/hr_employee.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
