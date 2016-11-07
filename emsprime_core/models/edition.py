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

class EmsEdition(models.Model):
    _name = 'ems.edition'

    code = fields.Char('Code', size=8, required=True)
    name = fields.Char('Name', size=32, required=True)
    start_date = fields.Date(
        'Start Date', required=True, default=datetime.now().date())
    end_date = fields.Date('End Date', required=True)
    reference_date = fields.Date('Reference Date')
    course_id = fields.Many2one('ems.course', 'Course', required=True)
    university_center_id = fields.Many2one('ems.university.center', 'University Center')
    subject_line = fields.One2many('ems.edition.subject', 'edition_id', string="Subject(s)", copy=True)
    course_plan_id = fields.Many2one('ems.course.plan', 'Course Plan')

    @api.one
    def copy(self, default=None):
        default = dict(default or {}, name=_("%s - copy") % self.name)
        return super(EmsEdition, self).copy(default=default)

    @api.one
    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        start_date = fields.Date.from_string(self.start_date)
        end_date = fields.Date.from_string(self.end_date)
        if start_date > end_date:

            raise ValidationError("End Date cannot be set before Start Date.")

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ This function filters editions list 
        """
        """ Below section is to filter Editions on Ems Class:
        """
        context = self._context or {}
        user = context.get('uid', False)
        if context and 'ems_class_filter_by_course' in context and context['ems_class_filter_by_course'] is True:
            course_id = context['course_id']
            if course_id:
                query = """select id from ems_edition where course_id=%s"""%(course_id)
                self._cr.execute(query)
                result = self._cr.fetchall()
                editions = []
                for res in result:
                    res = list(res)
                    editions.append(res[0])
                if editions:
                    args += [('id', 'in', editions)]
        return super(EmsEdition, self).search(args, offset, limit, order, count=count)


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self.env.context.get('get_parent_edition', False):
            lst = []
            lst.append(self.env.context.get('course_id'))
            courses = self.env['ems.course'].browse(lst)
            while courses.parent_id:
                lst.append(courses.parent_id.id)
                courses = courses.parent_id
            editions = self.env['ems.edition'].search([('course_id', 'in', lst)])
            return editions.name_get()

        """ Below section is to filter Editions on Ems Class:
        """
        context = self._context or {}
        user = context.get('uid', False)
        if context and 'ems_class_filter_by_course' in context and context['ems_class_filter_by_course'] is True:
            course_id = context['course_id']
            if course_id:
                query = """select id from ems_edition where course_id=%s"""%(course_id)
                self._cr.execute(query)
                result = self._cr.fetchall()
                editions = []
                for res in result:
                    res = list(res)
                    editions.append(res[0])
                if editions:
                    args += [('id', 'in', editions)]
        return super(EmsEdition, self).name_search(
            name, args, operator=operator, limit=limit)

    @api.onchange('course_id')
    @api.multi
    def onchange_course(self):
        vals = {}
        if not self.course_id:
            vals['subject_line'] = [[6, 0, []]]
            self.update(vals)
        else:
            lines = []
            for subject in self.course_id.subject_line:
                line_data = [0, False, {
                                'subject_id': subject.subject_id.id,
                                'week_work_load': subject.week_work_load,
                                'student_contact': subject.student_contact,
                                'work': subject.work,
                                'ects': subject.ects,
                                'semester': subject.semester
                            }]
                lines.append(line_data)
            vals['subject_line'] = lines
            self.update(vals)

    @api.multi
    def reload_subjects(self):
        for edition in self:
            self.subject_line.unlink()
            for subject in edition.course_id.subject_line:
                self.env['ems.edition.subject'].create({
                    'edition_id': edition.id,
                    'subject_id': subject.subject_id.id,
                    'week_work_load': subject.week_work_load,
                    'student_contact': subject.student_contact,
                    'work': subject.work,
                    'ects': subject.ects,
                    'semester': subject.semester
                })

    @api.multi
    def do_student_inscriptions(self):
        """Function to generate Inscription type of Enrollments for Students with Validated Matricula Enrollment
        """
        for edition in self:
            course_id = edition.course_id.id
            start_year = datetime.strptime(edition.start_date, "%Y-%m-%d").year
            end_year = datetime.strptime(edition.end_date, "%Y-%m-%d").year
            current_year = datetime.now().date().year
            if end_year < current_year:
                current_year = end_year
            diff = current_year - start_year
            if diff > 0:
                enrollments = self.env['ems.enrollment'].search([('edition_id','=',edition.id),
                                                                 ('type','=','M'),
                                                                 ('state','=','validate')])
                students, enrollments2 = [], []
                for enrollment in enrollments:
                    student_id = enrollment.student_id.id
                    inscr_enrollment = self.env['ems.enrollment'].search([('edition_id','=',edition.id),
                                                                          ('student_id','=',student_id),
                                                                          ('type','=','I')])
                    if not inscr_enrollment:
                        students.append(enrollment.student_id.id)
                        enrollments2.append(enrollment)

                for enrollment in enrollments2:
                    for academic_year in range(0, diff):
                        count = academic_year * 2
                        sem1, sem2 = count + 1, count + 2
                        subjects = []
                        subjects2 = [subjects.append(line.subject_id.id) for line in enrollment.course_id.subject_line \
                                     if line.semester in (str(sem1), str(sem2))]
                        enrollment_data = {
                                'roll_number': str(enrollment.roll_number) + '.' + str(start_year + academic_year),
                                'student_id': enrollment.student_id.id,
                                'type': 'I',
                                'course_id': enrollment.course_id.id,
                                'edition_id': enrollment.edition_id.id,
                                'subject_ids': [[6,0,subjects]],
                                'academic_year': str(start_year + academic_year),
                        }
                        ctx = dict(self._context)
                        ctx['no_rollno'] = True
                        ctx_inscription = ctx.copy()
                        inscription_id = self.env['ems.enrollment'].with_context(ctx_inscription).create(enrollment_data)
                        for subject in subjects:
                            course_id = enrollment.course_id.id
                            course = self.env['ems.course.subject'].search([('subject_id','=',subject), ('course_id','=',course_id)])
                            semester = course.semester
                            vals = {'subject_id': subject, 'inscription_id': inscription_id.id, 'semester': semester}
                            self.env['ems.enrollment.inscription.subject'].create(vals)


class EmsEditionSubject(models.Model):
    _name = "ems.edition.subject"
    _description = "Edition Subjects"
    _rec_name = "subject_id"
    _order = "course_year,semester,subject_id"

    #JCF - 12-09-2016
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
		
    #JCF - 09-09-2016
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

    edition_id = fields.Many2one('ems.edition', string='Edition')
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
    course_year = fields.Char(string='Course Year', compute='_get_course_year', store=True)
    course_report = fields.Char('Course Report')
    course_semester = fields.Char(string='Course Semester', compute='_get_semester_course', store=True)
    semester_report = fields.Char('Semester Report')
    ordering = fields.Integer('Ordering')

    _sql_constraints = [('uniq_edition_subject','unique(edition_id, subject_id)','Subject must be Unique per Edition.')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
