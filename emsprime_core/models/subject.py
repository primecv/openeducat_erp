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

class EmsSubject(models.Model):
    _name = 'ems.subject'
    _order = "name"

    name = fields.Char('Name', size=128, required=True)
    code = fields.Char('Code', size=256, required=True)
    course_id = fields.Many2one('ems.course', 'Course')
    grade_weightage = fields.Float('Grade Weightage')
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
    type = fields.Selection(
        [('theory', 'Theory'), ('practical', 'Practical'),
         ('both', 'Both'), ('other', 'Other')],
        'Type', default="theory", required=True)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        """ This function filters subjects list on Student List - by course wizard 
        to show subjects from Inscriptions related to selected Course and/or Academic Year 
        and/or Course Year. (works on drop down option)
        """
        context = self._context or {}
        user = context.get('uid', False)
        if context and 'course_subject' in context and context['course_subject'] is True:
            course_id = context['course_id']
            query = """select id from ems_enrollment where course_id=%s and type='I'"""%(course_id)
            if context['academic_year']:
                query += "and academic_year='%s'"%(context['academic_year'])
            if context['course_year']:
                query += "and course_year='%s'"%(context['course_year'])
            self._cr.execute(query)
            result = self._cr.fetchall()
            inscriptions = []
            for res in result:
                res = list(res)
                inscriptions.append(res[0])

            subjects = []
            if inscriptions:
                query2 = """select i.subject_id from ems_subject s, ems_enrollment e, ems_enrollment_inscription_subject i 
                                where e.id=i.inscription_id and 
                                    s.id=i.subject_id and 
                                    e.id in {0}""".format(tuple(inscriptions))
                self._cr.execute(query2)
                result2 = self._cr.fetchall()
                
                for subject in result2:
                    subject = list(subject)
                    subjects.append(subject[0])

            args += [('id', 'in', subjects)]

        """ Below section is to filter Subjects on Ems Class based on Edition selected:
        """
        if context and 'ems_class_filter_by_edition' in context and context['ems_class_filter_by_edition'] is True:
            edition_id = context['edition_id']
            if edition_id:
                edition = self.env['ems.edition'].browse(edition_id)
                course_plan_id = edition.course_plan_id and edition.course_plan_id.id or False
                subjects = []
                if course_plan_id:
                    query = """select subject_id from ems_course_plan_subject where course_plan_id=%s"""%(course_plan_id)
                    self._cr.execute(query)
                    result = self._cr.fetchall()
                    
                    for res in result:
                        res = list(res)
                        subjects.append(res[0])
                args += [('id', 'in', subjects)]
        return super(EmsSubject, self).name_search(name, args, operator, limit)

    @api.multi
    @api.constrains('name')
    def _check_name(self):
        for subject in self:
            subjects = self.search([('id','!=',self.id)])
            subject_list = []
            for all_subject in subjects:
                subject_list.append(all_subject.name.strip().lower())
            if subject.name.strip().lower() in subject_list:
                raise ValidationError(_('Subject "%s" already Exists.')%(subject.name.lower()))

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ This function filters subjects list on Student List - by course wizard 
        to show subjects from Inscriptions related to selected Course. (works on "Search More..." wizard)
        """
        context = self._context or {}
        user = context.get('uid', False)
        if context and 'course_subject' in context and context['course_subject'] is True:
            course_id = context['course_id']
            query = """select id from ems_enrollment where course_id=%s and type='I'"""%(course_id)
            if context['academic_year']:
                query += "and academic_year='%s'"%(context['academic_year'])
            if context['course_year']:
                query += "and course_year='%s'"%(context['course_year'])
            self._cr.execute(query)
            result = self._cr.fetchall()
            inscriptions = []
            for res in result:
                res = list(res)
                inscriptions.append(res[0])

            subjects = []
            if inscriptions:
                query2 = """select i.subject_id from ems_subject s, ems_enrollment e, ems_enrollment_inscription_subject i 
                                where e.id=i.inscription_id and 
                                    s.id=i.subject_id and 
                                    e.id in {0}""".format(tuple(inscriptions))
                self._cr.execute(query2)
                result2 = self._cr.fetchall()
                
                for subject in result2:
                    subject = list(subject)
                    subjects.append(subject[0])

            args += [('id', 'in', subjects)]
        
        """ Below section is to filter Subjects on Ems Class based on Edition selected:
        """
        if context and 'ems_class_filter_by_edition' in context and context['ems_class_filter_by_edition'] is True:
            edition_id = context['edition_id']
            if edition_id:
                edition = self.env['ems.edition'].browse(edition_id)
                course_plan_id = edition.course_plan_id and edition.course_plan_id.id or False
                subjects = []
                if course_plan_id:
                    query = """select subject_id from ems_course_plan_subject where course_plan_id=%s"""%(course_plan_id)
                    self._cr.execute(query)
                    result = self._cr.fetchall()
                    
                    for res in result:
                        res = list(res)
                        subjects.append(res[0])
                args += [('id', 'in', subjects)]
        return super(EmsSubject, self).search(args, offset, limit, order, count=count)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
