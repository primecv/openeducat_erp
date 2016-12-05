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


class WizardOpStudent(models.TransientModel):
    _name = 'wizard.ems.student'
    _description = "Create User for selected Student(s)"

    def _get_students(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    student_ids = fields.Many2many(
        'ems.student', default=_get_students, string='Students')

    @api.one
    def create_student_user(self):
        user_group = self.env.ref('emsprime_core.group_ems_student')
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['ems.student'].browse(active_ids)
        for student in records:
            if not student.email:
                raise ValidationError(_('Missing Institutional Email!\n\Student must have Institutional email to set Related Users Login id.\n\Student : %s')%(student.complete_name))
            user = self.env['res.users'].create_user([student], user_group)
            if user:
                student.write({'user_id': user.id})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
