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

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import datetime

class EmsScholarship(models.Model):
    _name = 'ems.scholarship'

    name = fields.Char('Name')
    start_date = fields.Date(
        'Start Date', required=False, default=datetime.today().date())
    end_date = fields.Date('End Date', required=False)
    student_id = fields.Many2one('ems.student', 'Student', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
