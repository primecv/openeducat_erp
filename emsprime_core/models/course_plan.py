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
import math

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime

class EmsCoursePlan(models.Model):
    _name = 'ems.course.plan'

    code = fields.Char('Code', size=12, required=True)
    name = fields.Char('Name', size=255, required=True)
    start_date = fields.Date(
        'Start Date', required=True, default=datetime.now().date())
    end_date = fields.Date('End Date')
    course_id = fields.Many2one('ems.course', 'Course', required=True)
    subject_line = fields.One2many('ems.course.plan.subject', 'course_plan_id', string="Subject(s)", copy=True)
    parent_id = fields.Many2one('ems.course.plan', 'Parent')
    state = fields.Selection(
        [('draft', 'New'), ('validate', 'Validated')],
        'State', default="draft", required=True, track_visibility='onchange', select=True)    

    @api.multi
    def action_draft(self):
        return self.write({'state':'draft'})

    @api.multi
    def action_validate(self):
        return self.write({'state':'validate'})

    @api.one
    def copy(self, default=None):
        default = dict(default or {}, name=_("%s - copy") % self.name)
        return super(EmsCoursePlan, self).copy(default=default)

    #@api.one
    #@api.constrains('start_date', 'end_date')
    #def check_dates(self):
    #    start_date = fields.Date.from_string(self.start_date)
    #    end_date = fields.Date.from_string(self.end_date)
    #    if start_date > end_date:
    #        raise ValidationError("End Date cannot be set before Start Date.")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_parent_course_plan', False):
            lst = []
            lst.append(self.env.context.get('course_id'))
            courses = self.env['ems.course'].browse(lst)
            while courses.parent_id:
                lst.append(courses.parent_id.id)
                courses = courses.parent_id
            course_plans = self.env['ems.course.plan'].search([('course_id', 'in', lst)])
            return course_plans.name_get()
        return super(EmsCoursePlan, self).name_search(
            name, args, operator=operator, limit=limit)

    @api.multi
    def load_subjects(self):
        courses = self.env['ems.course'].search([])
        for course in courses:
            for course_plan in course.course_plan_line:
                course_plan_id=course_plan.id
                editions = self.env['ems.edition'].search([('course_id','=',course.id)])
                for edition in editions:
                    for edition_subject in edition.subject_line:
                        edition_subject_id=edition_subject.id
                        subject_id=edition_subject.subject_id.id
                        self._cr.execute("""select count(*) as count from ems_course_plan_subject WHERE course_plan_id=%s and subject_id=%s"""%(course_plan_id,subject_id))
                        result = self._cr.fetchone()
                        if result:
                            result = result[0]
                            if result == 0:
                                self.env['ems.course.plan.subject'].create({
                                    'course_plan_id': course_plan_id,
                                    'subject_id': subject_id,
                                    'week_work_load': edition_subject.week_work_load,
                                    'student_contact': edition_subject.student_contact,
                                    'work': edition_subject.work,
                                    'ects': edition_subject.ects,
                                    'semester': edition_subject.semester,
                                    'ordering': edition_subject.ordering
                                })

class EmsCoursePlanSubject(models.Model):
    _name = "ems.course.plan.subject"
    _description = "Course Plans Subjects"
    _rec_name = "subject_id"
    _order = "course_year,semester,ordering"

    #JCF - 15-09-2016
    @api.one
    @api.depends('semester')
    def _get_course_year(self):
        semester = 0
        year = 0.0
        year_str = ''
        semester = int(self.semester)
        if semester > 0:
            year = semester / (2 * 1.0)
            year = math.ceil(year)
        year_str = str(int(year))	
        self.course_year = year_str

    #JCF - 15-09-2016
    @api.one
    @api.depends('semester')
    def _get_semester_course(self):
        semester = 0
        semester_str = ''
        semester = int(self.semester)
        if semester > 0:
            if semester % 2 == 0:
                semester=2
            else:
                semester=1
        semester_str = str(int(semester))
        self.semester_year = semester_str

    course_plan_id = fields.Many2one('ems.course.plan', string='Course Plan')
    subject_id = fields.Many2one('ems.subject', string='Subject')
    week_work_load = fields.Float('CHS', help='Weekly Work Load')
    student_contact = fields.Float('Contact', help='Hours of Contact with Student')
    work = fields.Integer('Work')
    ects = fields.Integer('ECTS')
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
    ordering = fields.Integer('Ordering')
    course_year = fields.Char(string='Course Year', compute='_get_course_year', store=True)
    course_report = fields.Char('Course Report')
    course_semester = fields.Char(string='Course Semester', compute='_get_semester_course', store=True)
    semester_report = fields.Char('Semester Report')
    optional = fields.Boolean('Optional')

    _sql_constraints = [('uniq_course_plan_subject','unique(course_plan_id, subject_id)','Subject must be Unique per Course Plan.')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
