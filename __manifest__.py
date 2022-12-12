# -*- coding: utf-8 -*-
{
    'name': "climbing_gym_access_list",

    'summary': """
       Climbing gym control control""",

    'description': """
        Climbing gym access list system to be used in:
            - climbing wall
            - courses
    """,

    'author': "Miguel Hatrick",
    'website': "https://www.dacosys.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Administration',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'climbing_gym',
                'climbing_gym_school',
                ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'data/cron_jobs.xml',

        'views/access_list.xml',
        'views/access_list_content.xml',
        'views/access_list_generator.xml',
        'views/menu.xml',

        'views/report/access_list_report.xml',

        'views/portal/portal_layout_sidebar.xml'

    ],
}
