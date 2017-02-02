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


class EmsEvaluationAttendees(models.Model):
    _name = 'ems.evaluation.attendee'
    _rec_name = 'student_id'

    @api.one
    @api.depends('marks')
    def _get_grade_str(self):
        grade_str=''
        if self.marks:
            grade_int=int(self.marks)
            print "GRADE INT::::::::::::::::::::::::::::::::::::::"
            print grade_int
            if grade_int==1:
                grade_str = "1 (Um)"
            elif grade_int ==2:
                grade_str = "2 (Dois)"
            elif grade_int ==3:
                grade_str = "3 (Três)"
            elif grade_int ==4:
                grade_str = "4 (Quatro)"
            elif grade_int ==5:
                grade_str = "5 (Cinco)"
            elif grade_int ==6:
                grade_str = "6 (Seis)"
            elif grade_int ==7:
                grade_str = "7 (Sete)"
            elif grade_int ==8:
                grade_str = "8 (Oito)"
            elif grade_int ==9:
                grade_str = "9 (Nove)"
            elif grade_int ==10:
                grade_str = "10 (Dez)"
            elif grade_int ==11:
                grade_str = "11 (Onze)"
            elif grade_int ==12:
                grade_str = "12 (Doze)"
            elif grade_int ==13:
                grade_str = "13 (Treze)"
            elif grade_int ==14:
                grade_str = "14 (Quatorze)"
            elif grade_int ==15:
                grade_str = "15 (Quinze)"
            elif grade_int ==16:
                grade_str = "16 (Dezasseis)"
            elif grade_int ==17:
                grade_str = "17 (Dezassete)"
            elif grade_int ==18:
                grade_str = "18 (Dezoito)"
            elif grade_int ==19:
                grade_str = "19 (Dezanove)"
            elif grade_int ==20:
                grade_str = "20 (Vinte)"
        else:
            grade_str = "a)"
        self.marks_string = grade_str

    student_id = fields.Many2one('ems.student', 'Student', required=True)
    status = fields.Selection(
        [('present', 'Present'), ('absent', 'Absent')],
        'Status', default="present", required=True)
    marks = fields.Float('Marks')
    note = fields.Text('Note')
    evaluation_id = fields.Many2one('ems.evaluation', 'Exam', required=True)
    course_id = fields.Many2one('ems.course', 'Course')
    edition_id = fields.Many2one('ems.edition', 'Edition')
    #marks_string = fields.Char('Marks (String)')
    marks_string = fields.Char(string='Grade (String)', compute='_get_grade_str', store=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
