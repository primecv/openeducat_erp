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
from lxml import etree

class EmsCourse(models.Model):
    _name = 'ems.course'

    name = fields.Char('Name', size=124, required=True)
    code = fields.Char('Code', size=8, required=True)
    parent_id = fields.Many2one('ems.course', 'Parent Course')
    section = fields.Char('Section', size=32, required=True)
    evaluation_type = fields.Selection(
        [('normal', 'Normal'), ('GPA', 'GPA'), ('CWA', 'CWA'), ('CCE', 'CCE')],
        'Evaluation Type', default="normal", required=True)
    subject_ids = fields.Many2many('ems.subject', string='Subject(s)')
    subject_line = fields.One2many('ems.course.subject', 'course_id', string="Subject(s)")
    degree_id = fields.Many2one('ems.course.degree', 'Degree')
    active = fields.Boolean(string="Active", default=True)
    attachment_line = fields.One2many('ems.attachment', 'course_id', 'Attachments')
    is_active = fields.Boolean('Is Active for Enrollment?', default=False)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Dynamically format Degree Filters To Course search view
        """
        res = super(EmsCourse, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'search':
            degree_ids = self.env['ems.course.degree'].search([('id','>',0)])
            degrees, degree_ref = [], []
            if degree_ids:
                for degree in degree_ids:
                    degrees.append(degree.name)
                    degree_ref.append(degree.id)
                for r in range(0, len(degrees)):
                    doc = etree.XML(res['arch'])
                    sfilter = etree.Element('filter')
                    sfilter.set('string', degrees[r])
                    sfilter.set('domain', "[('degree_id','=',%s)]"%(degree_ref[r]))
                    node = doc.xpath("//field[@name='parent_id']")
                    node[0].addnext(sfilter)
                    res['arch'] = etree.tostring(doc)
        return res

class EmsCourseSubject(models.Model):
    _name = "ems.course.subject"
    _description = "Course Subjects"
    _order = "semester"

    course_id = fields.Many2one('ems.course', string='Course')
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

    _sql_constraints = [('uniq_course_subject','unique(course_id, subject_id)','Subject must be Unique per Course.')]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
