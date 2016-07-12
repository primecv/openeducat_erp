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


class EmsEdition(models.Model):
    _name = 'ems.edition'

    code = fields.Char('Code', size=8, required=True)
    name = fields.Char('Name', size=32, required=True)
    start_date = fields.Date(
        'Start Date', required=True, default=fields.Date.today())
    end_date = fields.Date('End Date', required=True)
    course_id = fields.Many2one('ems.course', 'Course', required=True)
    university_center_id = fields.Many2one('ems.university.center', 'University Center')
    subject_line = fields.One2many('ems.edition.subject', 'edition_id', string="Subject(s)")

    @api.one
    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        start_date = fields.Date.from_string(self.start_date)
        end_date = fields.Date.from_string(self.end_date)
        if start_date > end_date:
            raise ValidationError("End Date cannot be set before Start Date.")

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
        return super(EmsEdition, self).name_search(
            name, args, operator=operator, limit=limit)

    @api.model
    def create(self, vals):
        """Mark Related course as Active if condition matched.
        """
        course_id = vals.get('course_id', False)
        if course_id:
            if vals['start_date'] > fields.Date.today():
                self.env.cr.execute("""update ems_course set is_active=True where id=%s"""%(course_id))
        return super(EmsEdition, self).create(vals)

    @api.multi
    def write(self, vals):
        """Mark Related course as Active if condition matched.
        """
        for edition in self:
            start_date = edition.start_date
            new_start_date = False
            if 'start_date' in vals:
                new_start_date = vals['start_date']
            course_id = edition.course_id.id
            new_course_id = False
            if 'course_id' in vals:
                new_course_id = vals['course_id']

            state = False
            if new_start_date:
                if new_start_date > fields.Date.today():
                    state = True
            else:
                if start_date > fields.Date.today():
                    state = True

            if new_course_id:
                self.env.cr.execute("""update ems_course set is_active=%s where id=%s"""%(state, new_course_id))
                self.env.cr.execute("""update ems_course set is_active=False where id=%s"""%(course_id))
            else:
                self.env.cr.execute("""update ems_course set is_active=%s where id=%s"""%(state, course_id))
        return super(EmsEdition, self).write(vals)

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

class EmsEditionSubject(models.Model):
    _name = "ems.edition.subject"
    _description = "Edition Subjects"

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

    _sql_constraints = [('uniq_edition_subject','unique(edition_id, subject_id)','Subject must be Unique per Edition.')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
