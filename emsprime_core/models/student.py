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
from lxml import etree

@api.model
def _lang_get(self):
    languages = self.env['res.lang'].search([])
    return [(language.code, language.name) for language in languages]

class EmsStudent(models.Model):
    _name = 'ems.student'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['ir.needaction_mixin', 'mail.thread']
    _rec_name = "complete_name"
    _description = "Student"

    @api.one
    @api.depends('name', 'middle_name', 'last_name')
    def _get_complete_name(self):
        self.complete_name = ' '.join(filter(bool, [self.name, self.middle_name, self.last_name]))

    @api.one
    @api.depends('roll_number_line')
    def _get_curr_enrollment(self):
        self.roll_number = ''
        self.course_id = False
        self.edition_id = False
        self.type_current_enroll = ''
        #check current date with the latest enrollment edition:
        count = 0
        for enrollment in self.roll_number_line:
            if count == 0:
                edition_id = enrollment.edition_id.id
                course_id = enrollment.course_id.id
                roll_number = enrollment.roll_number
                type_current_enroll = enrollment.type

                start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                count = count + 1
            else:
                if start_date < datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date():
                    start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                    edition_id = enrollment.edition_id.id
                    course_id = enrollment.course_id.id
                    roll_number = enrollment.roll_number
                    type_current_enroll = enrollment.type
            if type_current_enroll=='C':
                type_current_enroll='Candidatura'
            else:
                type_current_enroll='Matricula'

            self.roll_number = roll_number
            self.edition_id = edition_id
            self.course_id = course_id
            self.type_current_enroll = type_current_enroll

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
    nationality = fields.Many2one('ems.location', 'Nationality')
    emergency_contact = fields.Many2one(
        'res.partner', 'Emergency Contact')
    visa_info = fields.Char('Visa Info', size=64)
    id_number = fields.Char('ID Card Number', size=64)
    passport_no = fields.Char('Passport/BI', size=20)
    photo = fields.Binary('Photo')
    lang = fields.Selection(_lang_get, 'Language', default='pt_PT')
    course_ids = fields.Many2many('ems.course', 'ems_student_course_rel', 'student_id', 'course_id', 'Course(s)')
    #edition_id = fields.Many2one('ems.edition', 'Edition', required=False)
    roll_number_line = fields.One2many(
        'ems.enrollment', 'student_id', 'Roll Number')
    partner_id = fields.Many2one(
        'res.partner', 'Partner', required=True, ondelete="cascade")

    roll_number = fields.Char(string='Current Roll Number', compute='_get_curr_enrollment', store=True, track_visibility='onchange')
    course_id = fields.Many2one('ems.course', string='Course', compute='_get_curr_enrollment', store=True, track_visibility='onchange')
    edition_id = fields.Many2one('ems.edition', string='Edition', compute='_get_curr_enrollment', store=True, track_visibility='onchange')

    gr_no = fields.Char("GR Number", size=20)
    location_id = fields.Many2one('ems.location', 'Place of birth')
    mother = fields.Char('Mother', size=255)
    father = fields.Char('Father', size=255)
    issuer = fields.Char('Issuer')
    issue_date = fields.Date('Issue Date')
    institutional_email = fields.Char('Institutional email', size=128)
    complete_name = fields.Char('Name', compute='_get_complete_name', store=True, track_visibility='onchange')
    attachment_line = fields.One2many('ems.attachment', 'student_id', 'Attachments')
    country_id = fields.Many2one('ems.location', 'Country')
    island_id = fields.Many2one('ems.location', 'Island')
    county_id = fields.Many2one('ems.location', 'County')
    parish_id = fields.Many2one('ems.location', 'Parish')
    app_course_year = fields.Char("Course/Year", size=255)
    app_course_academic_year = fields.Char("Academic Year", size=64)
    app_course_area = fields.Char("Area", size=255)
    math_final_average = fields.Float('Math Final Average')
    course_option_1 = fields.Many2one('ems.course', 'Course - Option 1')
    course_option_2 = fields.Many2one('ems.course', 'Course - Option 2')
    course_option_3 = fields.Many2one('ems.course', 'Course - Option 3')
    high_school_score = fields.Char('High School')
    schedule_choice = fields.Selection(
        [('morning', 'Morning'), ('afternoon', 'Afternoon'),
         ('evening', 'Evening')],
        'Schedule Choice', default="morning")
    sponsorship = fields.Selection(
        [('own_expenses', 'Own Expenses'), ('scholarship', 'Scholarship'),
         ('company', 'Company')],
        'Sponsorship', default="own_expenses")		
    state = fields.Selection([('draft', 'New'),
                              ('submit', 'Submitted'),
                              ('received', 'Received'),
                              ('confirmed', 'Accepted'),
                              ('rejected', 'Rejected')], 'State', default='draft', track_visibility='onchange')
    #Permanant Address fields:
    pstreet = fields.Char('Street')
    pstreet2 = fields.Char('Street2')
    pcity = fields.Char('City')
    pzip = fields.Char('PostCode')
    acountry_id = fields.Many2one('ems.location', 'Country')
    pcountry_id = fields.Many2one('ems.location', 'Country')
    portuguese_final_average = fields.Float('Average Portuguese')
    final_average = fields.Float('Final Average')
    university_center_id = fields.Many2one('ems.university.center', 'University Center')
    type_current_enroll = fields.Char(string='Type of current enrollment', compute='_get_curr_enrollment', store=True)
	
    @api.one
    @api.constrains('birth_date')
    def _check_birthdate(self):
        if self.birth_date > fields.Date.today():
            raise ValidationError(
                "Birth Date can't be greater than current date!")

    @api.onchange('country_id')
    def _onchange_country(self):
        self.island_id = False
        self.county_id = False
        self.parish_id = False

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        user = context.get('uid', False)
        imd = self.env['ir.model.data']
        student_access_groups = ['emsprime_core.group_ems_faculty', 
                                 'emsprime_core.group_ems_back_office', 
                                 'emsprime_core.group_ems_back_office_admin' ]
        allowed_group_ids = []
        for group in student_access_groups:
            group_id = imd.xmlid_to_res_id(group)
            if group_id:
                allowed_group_ids.append(group_id)
        user_groups = []
        groups = [user_groups.append(group.id) for group in self.env['res.users'].browse(user).groups_id]
        student_read = False
        for user_group in user_groups:
            if user_group in allowed_group_ids:
                student_read = True
        if not student_read and user:
            self._cr.execute(""" select id from ems_student where create_uid=%s and state='draft' """%(user))
            student_list = [r[0] for r in self._cr.fetchall()]
            args += [('id', 'in', student_list)]
        return super(EmsStudent, self).search(args, offset, limit, order, count=count)

    @api.multi
    def action_submit(self):
        return self.write({'state': 'submit'})

    @api.multi
    def action_received(self):
        for student in self:
            if not student.course_option_1:
                raise ValidationError('Missing Course Option 1.')
            course_id = student.course_option_1.id
            editions = self.env['ems.edition'].search([('course_id','=',course_id)], limit=1)
            edition_id = False
            for edition in editions:
               edition_id = edition.id
            if course_id and edition_id:
                enrollment_id = self.env['ems.enrollment'].create({'course_id': course_id, 
                                                                   'edition_id': edition_id,
                                                                   'student_id': student.id,
                                                                   'type': 'C'})
        return self.write({'state': 'received'})

    @api.multi
    def action_confirm(self):
        return self.write({'state': 'confirmed'})

    @api.multi
    def action_reject(self):
        return self.write({'state': 'rejected'})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
