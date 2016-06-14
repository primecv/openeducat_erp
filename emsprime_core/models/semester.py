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


class EmsSemester(models.Model):
    _name = 'ems.semester'

    @api.one
    @api.depends('semester')
    def _get_name(self):
        self.name = str(self.semester) + 'º' + ' Semester'

    name = fields.Char('Name', compute='_get_name', store=True)
    start_date = fields.Date(
        'Start Date', required=False, default=fields.Date.today())
    end_date = fields.Date('End Date', required=False)
    number= fields.Integer('Number')
    code = fields.Char('Code')
    course_id = fields.Many2one('ems.course', 'Course', required=True)
    edition_id = fields.Many2one('ems.edition', 'Edition', required=True)
    #course_id = fields.Many2one('ems.course', string='Course', related='edition_id.course_id', store=True, readonly=True)
    subject_ids = fields.Many2many('ems.subject', 'ems_semester_subject_rel', 'semester_id', 'subject_id', string='Subjects')
    subject_line = fields.One2many('ems.semester.subject', 'semester_id', 'Subjects')
    semester = fields.Selection([('1', '1'), 
                                ('2', '2'), 
                                ('3', '3'),
                                ('4', '4'),
                                ('5', '5'),
                                ('6', '6'),
                                ('7', '7'),
                                ('8', '8'),
                                ('9', '9')

            ], 'Semester')
    year = fields.Char('Year', size=4)

class EmsSemesterSubject(models.Model):
    _name = "ems.semester.subject"
    _description = "Semester Subjects"

    semester_id = fields.Many2one('ems.semester', 'Semester')
    subject_id = fields.Many2one('ems.subject', 'Subject')
    week_work_load = fields.Float('CHS', help='Weekly Work Load')
    student_contact = fields.Float('Contact', help='Hours of Contact with Student')
    ects = fields.Integer('ECTS')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
