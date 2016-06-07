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
from datetime import datetime, date

class EmsStudent(models.Model):
    _name = 'ems.student'
    _inherits = {'res.partner': 'partner_id'}

    @api.one
    @api.depends('roll_number_line')
    def _get_curr_enrollment(self):
        self.roll_number = ''
        self.course_id = False
        self.edition_id = False
        #check current date with the latest enrollment edition:
        count = 0
        for enrollment in self.roll_number_line:
            if count == 0:
                edition_id = enrollment.edition_id.id
                course_id = enrollment.course_id.id
                roll_number = enrollment.roll_number

                start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                count = count + 1
            else:
                if start_date < datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date():
                    start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                    edition_id = enrollment.edition_id.id
                    course_id = enrollment.course_id.id
                    roll_number = enrollment.roll_number
            self.roll_number = roll_number
            self.edition_id = edition_id
            self.course_id = course_id

    middle_name = fields.Char('Middle Name', size=128)
    last_name = fields.Char('Last Name', size=128, required=True)
    birth_date = fields.Date('Birth Date', required=False)
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        'Blood Group')
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female'),
         ('o', 'Other')], 'Gender', required=True)
    nationality = fields.Many2one('res.country', 'Nationality')
    emergency_contact = fields.Many2one(
        'res.partner', 'Emergency Contact')
    visa_info = fields.Char('Visa Info', size=64)
    id_number = fields.Char('ID Card Number', size=64)
    photo = fields.Binary('Photo')
    course_ids = fields.Many2many('ems.course', 'ems_student_course_rel', 'student_id', 'course_id', 'Course(s)')
    #edition_id = fields.Many2one('ems.edition', 'Edition', required=False)
    roll_number_line = fields.One2many(
        'ems.enrollment', 'student_id', 'Roll Number')
    partner_id = fields.Many2one(
        'res.partner', 'Partner', required=True, ondelete="cascade")

    roll_number = fields.Char(string='Current Roll Number', compute='_get_curr_enrollment', store=True)
    course_id = fields.Many2one('ems.course', string='Course', compute='_get_curr_enrollment', store=True)
    edition_id = fields.Many2one('ems.edition', string='Edition', compute='_get_curr_enrollment', store=True)

    gr_no = fields.Char("GR Number", size=20)
    location_id = fields.Many2one('ems.location', 'Place of birth')
    mother = fields.Char('Mother', size=255)
    father = fields.Char('Father', size=255)
    issuer_id = fields.Many2one('ems.location', 'Issuer')

    @api.one
    @api.constrains('birth_date')
    def _check_birthdate(self):
        if self.birth_date > fields.Date.today():
            raise ValidationError(
                "Birth Date can't be greater than current date!")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
