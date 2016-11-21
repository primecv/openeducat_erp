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
from openerp.tools.translate import _

class WizardOpFaculty(models.TransientModel):
    _name = 'wizard.ems.faculty'
    _description = "Create User for selected Faculty(s)"

    def _get_faculties(self):
        if self.env.context and self.env.context.get('active_ids'):
            return self.env.context.get('active_ids')
        return []

    faculty_ids = fields.Many2many(
        'ems.faculty', default=_get_faculties, string='Faculties')

    @api.one
    def create_faculty_user(self):
        user_group = self.env.ref('emsprime_core.group_ems_faculty')
        active_ids = self.env.context.get('active_ids', []) or []
        records = self.env['ems.faculty'].browse(active_ids)
        for faculty in records:
            if not faculty.email:
                raise ValidationError(_('Missing Institutional Email!\n\nFaculty must have Institutional email to set Related Users Login id.\n\nFaculty : %s')%(faculty.complete_name))
            user = self.env['res.users'].create_faculty_user([faculty], user_group)
            if user:
                faculty.write({'user_id': user.id})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
