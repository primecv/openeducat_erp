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
from datetime import datetime


class EmsFaculty(models.Model):
    _name = 'ems.faculty'
    _inherits = {'res.partner': 'partner_id'}

    @api.one
    @api.depends('name', 'middle_name', 'last_name')
    def _get_complete_name(self):
        self.complete_name = ' '.join(filter(bool, [self.name, self.middle_name, self.last_name]))

    partner_id = fields.Many2one(
        'res.partner', 'Partner', required=True, ondelete="cascade")
    middle_name = fields.Char('Middle Name', size=128)
    last_name = fields.Char('Last Name', size=128, required=True)
    birth_date = fields.Date('Birth Date', required=True)
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        'Blood Group')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')], 'Gender', required=True)
    nationality = fields.Many2one('res.country', 'Nationality')
    emergency_contact = fields.Many2one(
        'res.partner', 'Emergency Contact')
    visa_info = fields.Char('Visa Info', size=64)
    id_number = fields.Char('ID Card Number', size=64)
    photo = fields.Binary('Photo')
    login = fields.Char(
        'Login', related='partner_id.user_id.login', readonly=1)
    last_login = fields.Datetime(
        'Latest Connection', related='partner_id.user_id.login_date',
        readonly=1)
    location_id = fields.Many2one('ems.location', 'Place of birth')
    faculty_subject_ids = fields.Many2many('ems.subject', string='Subject(s)')
    emp_id = fields.Many2one('hr.employee', 'Employee')
    complete_name = fields.Char('Faculty Name', compute='_get_complete_name', store=True)
    institutional_email = fields.Char('Institutional email', size=128)
    degree_id = fields.Many2one('ems.course.degree', 'Degree')
    attachment_line = fields.One2many('ems.attachment', 'faculty_id', 'Attachments')
    country_id = fields.Many2one('ems.location', 'Country')
    island_id = fields.Many2one('ems.location', 'Island')
    county_id = fields.Many2one('ems.location', 'County')
    parish_id = fields.Many2one('ems.location', 'Parish')
    training_area_line = fields.One2many('ems.training.area', 'faculty_id', 'Training Areas')
    university_center_id = fields.Many2one('ems.university.center', 'University Center', track_visibility='onchange')
    code = fields.Char('Code', size=8, required=True)
    class_line = fields.One2many('ems.class', 'faculty_id', 'Classes')

    @api.one
    @api.constrains('birth_date')
    def _check_birthdate(self):
        if datetime.strptime(self.birth_date, '%Y-%m-%d').date() > datetime.now().date():
            raise ValidationError(
                "Birth Date can't be greater than current date!")

    @api.model
    def create(self, vals):
        res = super(EmsFaculty, self).create(vals)
        vals = {
            'name': res.name + ' ' + (res.middle_name or '') +
            ' ' + res.last_name,
            'country_id': res.nationality and res.nationality.id or False,
            'gender': res.gender,
            'address_home_id': res.partner_id.id
        }
        emp = self.env['hr.employee'].create(vals)
        self.write({'emp_id': emp.id})
        res.partner_id.write({'supplier': True, 'employee': True})
        return res

    @api.multi
    def name_get(self):
        result = []
        for faculty in self:
            name = ' '.join(filter(bool, [faculty.name, faculty.middle_name, faculty.last_name]))
            result.append((faculty.id, name))
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
