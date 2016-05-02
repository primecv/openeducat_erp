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
from openerp.tools.translate import _

class EmsClass(models.Model):
    _name = 'ems.class'

    @api.one
    @api.constrains('year')
    def _check_year(self):
        for year in self.year:
           if ord(year) not in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57):
               raise ValidationError(_("Invalid Year!\n\nYear must be between 2000 - 3000"))
        if int(self.year) > 3000 or int(self.year) < 2000:
           raise ValidationError(_("Invalid Date!"))

    name = fields.Char('Class Name', size=64, required=True)
    faculty_id = fields.Many2one('ems.faculty', 'Faculty', required=True)
    subject_id = fields.Many2one('ems.subject', 'Subject', required=True)
    student_ids = fields.Many2many('ems.student', string='Student(s)')
    semester_id = fields.Many2one('ems.semester', string='Semester')
    semester = fields.Selection([('I', 'I'), ('II', 'II')], 'Semester')
    year = fields.Char('Year', size=4)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
