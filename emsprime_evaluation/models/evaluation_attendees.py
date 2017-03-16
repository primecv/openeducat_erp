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
    _order = "student_id"

    @api.one
    @api.depends('marks','status')
    def _get_grade_str(self):
        grade_str=''
        grade_int=0
        grade_round=0.0
        if self.marks:
            grade_round=round(self.marks)
            grade_int=int(grade_round)
            if grade_int==1:
                grade_str = "1 (Um)"
            elif grade_int ==0:
                grade_str = "0 (Zero)"
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
                grade_str = "14 (Catorze)"
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
        elif self.status:
            grade_str = self.status
        else:
            grade_str = "a)"
        self.marks_string = grade_str
        self.marks_string2 = grade_str
        self.final_grade = grade_int

    @api.one
    @api.depends('evaluation_id')
    def _get_data(self):
        faculty_id = False
        subject_id = False
        class_id = False
        academic_year=''
        student_name=''
        faculty_name=''
        roll_number=''
        if self.evaluation_id:
            faculty_id=self.evaluation_id.faculty_id.id
            subject_id=self.evaluation_id.subject_id.id
            class_id=self.evaluation_id.class_id.id
            academic_year=self.evaluation_id.academic_year
            roll_number=self.student_id.roll_number
            student_name=self.student_id.complete_name
            faculty_name=self.evaluation_id.faculty_id.complete_name
        self.faculty_id=faculty_id
        self.subject_id=subject_id
        self.class_id=class_id
        self.academic_year=academic_year
        self.roll_number=roll_number
        self.student_name=student_name
        self.faculty_name=faculty_name

    @api.one
    @api.depends('marks')
    def _get_final_grade(self):
        final_grade=0
        round_grade=0.0
        if self.marks:
            round_grade=round(self.marks)
            final_grade=int(round_grade)
        self.final_grade=final_grade
		

    student_id = fields.Many2one('ems.student', 'Student', required=True)
    status = fields.Selection(
        [('F', 'Missed'), ('D', 'Gave up'), ('A', 'Nullified')],
        'Status')
    marks = fields.Float('Marks')
    note = fields.Text('Note')
    evaluation_id = fields.Many2one('ems.evaluation', 'Exam', required=True)
    course_id = fields.Many2one('ems.course', 'Course')
    edition_id = fields.Many2one('ems.edition', 'Edition')
    #marks_string = fields.Char('Marks (String)')
    marks_string = fields.Char(string='Grade (String)', compute='_get_grade_str', store=True)
    marks_string2 = fields.Char(string='Grade (String) 2', compute='_get_grade_str', store=True)
    faculty_id = fields.Many2one('ems.faculty', string='Faculty', compute='_get_data', store=True, track_visibility='onchange')
    subject_id = fields.Many2one('ems.subject', string='Subject', compute='_get_data', store=True, track_visibility='onchange')
    #student_id = fields.Many2one('ems.student', string='Student', compute='_get_data', store=True, track_visibility='onchange')
    academic_year = fields.Char('Academic Year', compute='_get_data', store=True, track_visibility='onchange')
    class_id = fields.Many2one('ems.class', string='Class', compute='_get_data', store=True, track_visibility='onchange')
    roll_number = fields.Char('Roll name', compute='_get_data', store=True, track_visibility='onchange')
    student_name = fields.Char('Student name', compute='_get_data', store=True, track_visibility='onchange')
    faculty_name = fields.Char('Faculty name', compute='_get_data', store=True, track_visibility='onchange')
    final_grade = fields.Integer('Final grade', compute='_get_final_grade', store=True, track_visibility='onchange')
    #JCF - 22-02-2017
    exam_type = fields.Many2one('ems.evaluation.type', related="evaluation_id.exam_type", string='Exam type', store=True, readonly=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
