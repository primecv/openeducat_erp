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

    '''@api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        context = self._context or {}
        if context and 'inscription' in context and 'edition_id' in context:
            edition_id = context['edition_id']
            edition = self.env['ems.edition'].browse(edition_id)
            subjects = []
            subject_list = [subjects.append(x.subject_id.id) for x in edition.subject_line]
            args = [['id', 'in', subjects]]
        return super(EmsSubject, self).name_search(name, args, operator, limit)'''

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
