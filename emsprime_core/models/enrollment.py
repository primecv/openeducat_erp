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
from datetime import datetime

class EmsEnrollment(models.Model):
    _name = 'ems.enrollment'
    _rec_name = 'roll_number'

    roll_number = fields.Char('Roll Number', size=15, required=True)
    course_id = fields.Many2one('ems.course', 'Course', required=True)
    edition_id = fields.Many2one('ems.edition', 'Edition', required=True)
    student_id = fields.Many2one('ems.student', 'Student', required=True)
    state = fields.Selection([('draft','New'),('validate','Validated')], string='State', default='draft')
    academic_year = fields.Char('Academic Year', size=4)
    subject_ids = fields.Many2many('ems.subject', 'ems_enrollment_subjects_rel', 'enrollment_id', 'subject_id', 'Subjects')
    type = fields.Selection(
        [ ('C', 'Candidatura'), ('I', 'Inscrição'), ('M', 'Matricula')], 'Tipo', required=True, default='M')

    @api.onchange('student_id')
    def onchange_student(self):
        #self.course_id = self.student_id.course_id
        if self.student_id.edition_id:
            self.update({'edition_id': self.student_id.edition_id})
        else:
            self.update({'edition_id': False})

    _sql_constraints = [
        ('unique_name_roll_number_id',
         'unique(roll_number,course_id,edition_id,student_id)',
         'Roll Number & Student must be unique per Edition!'),
        ('unique_name_roll_number_course_id',
         'unique(roll_number,course_id,edition_id)',
         'Roll Number must be unique per Edition!'),
        ('unique_name_roll_number_student_id',
         'unique(student_id,course_id,edition_id)',
         'Student must be unique per Edition!'),
    ]

    @api.model
    def create(self, vals):
        if 'type' in vals and vals['type'] == 'C':
            last_rec = self.search([('id','>',0),('roll_number','!=', '')], order='id desc', limit=1)
            next_seq = '00001'
            if last_rec:
                last_seq = last_rec.roll_number
                try:
                    seq = last_seq.split('.')[1]
                    next_seq = str(int(seq) + 1)
                    while len(next_seq) < 3:
                        next_seq = '0' + next_seq
                except Exception:
                    pass
            year = datetime.now().date().year
            idno = str(year) + '.' + next_seq
            vals['roll_number'] = idno
        return super(EmsEnrollment, self).create(vals)

    @api.multi
    def action_load_subjects(self):
        for enrollment in self:
            course_subjects = []
            subject_list = [course_subjects.append(x.subject_id.id) for x in enrollment.edition_id.course_id.subject_line]
            #subjects = []
            #for subject in enrollment.subject_ids:
            #    subjects.append(subject.id)
            #for subject in subjects:
            #    course_subjects.pop(course_subjects.index(subject))

            wiz_id = self.env['ems.enrollment.inscricao.subject'].create({})
            for subject in course_subjects:
                self.env['ems.enrollment.inscricao.subject.line'].create({'subject_id': subject, 'form_id': wiz_id.id})
            context = {}
            context['active_id'] = self.id
            context['active_model'] = self._name
            return {
                'name': ('Select Subjects'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ems.enrollment.inscricao.subject',
                'type': 'ir.actions.act_window',
                'res_id': wiz_id.id,
                'context': context,
                'target': 'new'
            }

    @api.one
    def action_validate(self):
        return self.write({'state': 'validate'})
            

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
