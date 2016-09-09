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

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from datetime import datetime

class EmsCoursePlan(models.Model):
    _name = 'ems.course.plan'

    code = fields.Char('Code', size=12, required=True)
    name = fields.Char('Name', size=255, required=True)
    start_date = fields.Date(
        'Start Date', required=True, default=fields.Date.today())
    end_date = fields.Date('End Date')
    course_id = fields.Many2one('ems.course', 'Course', required=True)
    subject_line = fields.One2many('ems.course.plan.subject', 'course_plan_id', string="Subject(s)", copy=True)
    parent_id = fields.Many2one('ems.course', 'Parent')

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



class EmsCoursePlanSubject(models.Model):
    _name = "ems.course.plan.subject"
    _description = "Course Plans Subjects"
    _rec_name = "subject_id"
    _order = "semester"

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

    _sql_constraints = [('uniq_course_plan_subject','unique(course_plan_id, subject_id)','Subject must be Unique per Course Plan.')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
