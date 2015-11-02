# -*- coding: utf-8 -*-
###############################################################################
#
#    Prime Consulting SA Cape Verde.
#    Copyright (C) 2009-TODAY Prime Consulting(<http://www.prime.cv>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'OpenEduCat ERP - ISCII',
    'version': '1.0',
    'category': 'ISCII Education',
    'summary': 'Manage Students, Faculties and Education Institute for ISCII',
    'complexity': "easy",
    'author': 'Prime Consulting, Cape Verde',
    'website': 'http://www.prime.cv',
    'depends': ['openeducat_erp', 'openeducat_core'],
    'data': [
            'op_course_view.xml',
            'op_course_data.xml',
            'data/op_subject_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
