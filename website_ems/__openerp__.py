# -*- coding: utf-8 -*-

{
    'name': 'Online EMS',
    'category': 'Openerp Education',
    'sequence': 1,
    'summary': 'Manage Students, Faculties and Education Institute',
    'website': 'https://www.prime.cv',
    'version': '1.0',
    'description': """
Manage Students, Faculties and Education Institute
        """,
    'depends': ['website', 'website_partner', 'website_mail', 'emsprime_core', 'emsprime_evaluation'],
    'data': [
        'data/student_data.xml',
        'views/website_ems.xml',
        'views/website_ems_backend.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'demo': [],
    'installable': True,
    'application': True,
}
