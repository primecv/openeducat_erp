# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'EMSPrime Core',
    'version': '1.0.0',
    'category': 'Openerp Education',
    "sequence": 1,
    'summary': 'Manage Students, Faculties and Education Institute',
    'complexity': "easy",
    'description': """
        This module provide core education management system over OpenERP
        Features includes managing
            * Student
            * Faculty
            * Course
            * Edition

    """,
    'author': 'Prime Consulting',
    'website': 'http://www.prime.cv',
    'depends': ['board', 'document', 'hr', 'web', 'website'],
    'data': [
        'report/layouts.xml',
        'report/report_student_bonafide.xml',
        'report/report_student_idcard.xml',
        'report/report_menu.xml',
        'wizard/faculty_create_employee_wizard_view.xml',
        'wizard/faculty_create_user_wizard_view.xml',
        'wizard/students_create_user_wizard_view.xml',
        'security/ems_security.xml',
        'security/ir.model.access.csv',
        'views/student_view.xml',
        'views/hr_view.xml',
        'views/location_view.xml',
        'views/attachment_type_view.xml',
        'views/attachment_view.xml',
        'views/training_area_view.xml',
        'views/university_center_view.xml',
        'views/course_view.xml',
        'views/edition_view.xml',
        'views/semester_view.xml',
        'views/subject_view.xml',
        'views/enrollment_view.xml',
        'views/student_status_view.xml',
        'views/scholarship_view.xml',
        'views/faculty_view.xml',
        'views/ems_class_view.xml',
        'views/ems_request_view.xml',
        'views/res_company_view.xml',
        'views/res_country_view.xml',
        'views/degree_view.xml',
        'views/emsprime_template.xml',
        'views/homepage_template.xml',
        'views/website_assets.xml',
        'dashboard/faculty_dashboard_view.xml',
        'dashboard/student_dashboard_view.xml',
        
        'data/degree.xml',
        'data/request.xml',
        'data/res_users.xml',

        'report/report_frequency_declaration.xml',
        'report/report_admissionreceipt.xml',
        'report/report_boletiminscription.xml',
        'report/enrollment_grades_report_view.xml',
        'report/report_enrollment_declaration.xml',
        'report/report_boletiminscription_request.xml',

        'wizard/ems_enrollment_inscricao_subject_view.xml',
        'menu/emsprime_core_menu.xml',
        'menu/faculty_menu.xml',
        'menu/student_menu.xml',
        #admin tools:
        'wizard/ems_enrollment_import_view.xml',
    ],
    'demo': [
        'demo/res.users.csv',
        'demo/res.groups.csv'
    ],
    'css': ['static/src/css/base.css'],
    'qweb': [
        'static/src/xml/base.xml'],
    'js': ['static/src/js/chrome.js'],
    'images': [
        'static/description/emsprime_core_banner.jpg',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
