# -*- coding: utf-8 -*-
###############################################################################
#
#    Prime Consulting SA
#    Copyright (C) 2016-TODAY Prime Consulting SA(<http://www.prime.cv>).
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
import math

from openerp import models, fields, api, _
from datetime import datetime
import base64, re
from openerp.exceptions import ValidationError, UserError

class ems_request_type(models.Model):
    _name = 'ems.request.type'
    _description = "Request Type"
    _order = 'name'
	
    name = fields.Char('Request Type', required=True)
    report_id = fields.Many2one('ir.actions.report.xml', 'Report')
    type = fields.Selection(
        [('S', 'Student'), ('F', 'Faculty')], 'Type', required=True, track_visibility='onchange')
    declaration_text = fields.Text('Declaration text')
    is_grade = fields.Boolean('Grades?')

class ems_request(models.Model):
    _name = "ems.request"
    _description = "Request"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    #JCF - 07-09-2016
    @api.one
    @api.depends('enrollment_id','faculty_id')
    def _get_student_faculty(self):
        str_name = ''
        if self.enrollment_id:
		    str_name=self.enrollment_id.student_id.roll_number
        else:
		    str_name=self.faculty_id.complete_name
        self.student_faculty = str_name
		
    #JCF - 06-09-2016
    @api.one
    @api.depends('enrollment_id')
    def _get_university_center(self):
        university_center_id = False
        #print "Student UNIVERSITY:: "
        #print self.enrollment_id.student_id.id
        if self.enrollment_id:
            enrollments = self.env['ems.enrollment'].search([('student_id','=',self.enrollment_id.student_id.id),('type','=','I')], order="id desc", limit=1)
            for enrollment in enrollments:
                university_center_id=enrollment.university_center_id.id
        else:
            university_center_id=self.faculty_id.university_center_id.id
        self.university_center_id = university_center_id
			
    #JCF - 05-09-2016
    @api.one
    @api.depends('enrollment_id')
    def _get_curr_inscription(self):
        current_inscription_id = False
        enrollments = self.env['ems.enrollment'].search([('student_id','=',self.enrollment_id.student_id.id),('type','=','I')])
        #check current date with the latest enrollment edition:
        count = 0
        for enrollment in enrollments:
            try:
                if count == 0:
                    current_inscription_id = enrollment.id

                    start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                    count = count + 1
                else:
                    if start_date <= datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date() and enrollment.type=='I':
                        start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                        current_inscription_id = enrollment.id
            except Exception:
                pass

            self.current_inscription_id = current_inscription_id

    name = fields.Char('Request Name', required=True, track_visibility='onchange', select=True)
    student_id = fields.Many2one('ems.student', 'Student', track_visibility='onchange')
    enrollment_id = fields.Many2one('ems.enrollment', 'Record Number', track_visibility='onchange', select=True)
    request_type_id = fields.Many2one('ems.request.type', string='Request Type', track_visibility='onchange', select=True)
    description = fields.Text('Special Mentions')
    date = fields.Date('Request Date', track_visibility="onchange", default=fields.date.today(), readonly=True)
    state = fields.Selection(
        [('draft', 'New Request'), ('validate', 'Processed'),
         ('pending', 'Pending'), ('done', 'Done')],
        'State', default="draft", required=True, track_visibility='onchange', select=True)
    sequence = fields.Char('Declaration Number')
    current_inscription_id = fields.Many2one('ems.enrollment', string='Current Inscription', compute='_get_curr_inscription', store=True, track_visibility='onchange')
    university_center_id = fields.Many2one('ems.university.center', string='University Center', compute='_get_university_center', store=True, track_visibility='onchange')
    year = fields.Char('Year of Declaration')
    number = fields.Char('Number of Declaration')
    #report_type = fields.Char(related='request_type_id.type', string='Roll number', store=False)
    report_type = fields.Selection(
        [('S', 'Student'), ('F', 'Faculty')], 'Type',related='request_type_id.type', track_visibility='onchange', store=False)
    faculty_id = fields.Many2one('ems.faculty', 'Faculty', track_visibility='onchange')
    regime = fields.Selection(
        [('24h', '24 horas'), ('48h', '48 horas'), ('72h', '72 horas'), ('normal', 'Normal')], 'Regime', required=True, track_visibility='onchange')
    student_faculty = fields.Char(string='Student/Faculty', compute='_get_student_faculty', store=True)
    processor_id = fields.Many2one('res.users', 'Processor', track_visibility='onchange', select=True)

    @api.model
    def create(self, vals):
        res = super(ems_request, self).create(vals)
        #get partners related to EmsPrime / Back Office Admin group users:
        backoffice_admin_groupid = self.env['ir.model.data'].xmlid_to_res_id('emsprime_core.group_ems_back_office_admin')
        users = []
        if backoffice_admin_groupid:
            for group in self.env['res.groups'].browse([backoffice_admin_groupid]):
                for user in group.users:
                    users.append(user.partner_id.id)
            if users:
                self.write({'message_follower_ids': [[6, 0, users]]})
        return res

    def get_to_year(self, year):
        if year:
           return int(year) + 1
        return None

    @api.multi
    def action_validate(self):
        """Generate sequence in "YYYY/0001" format by University center
        """
        year = datetime.now().date().year
        next_seq = str(year) + '/0001'
        str_number = '0001'
        if self.sequence:
            self.write({'state':'validate'})
        else:
            self._cr.execute("""select sequence from ems_request where university_center_id in (%s) and sequence ilike '%s%%' order by id desc limit 1"""%(self.university_center_id.id,str(year) + '/'))
            result = self._cr.fetchone()
            if result:
                result = result[0]
                result = str(result).split('/')
            if result and len(result) == 2:
                result = int(result[1])
                next_seq = str(result + 1)
                while len(next_seq) < 4:
                    next_seq = '0' + next_seq
                str_number = next_seq
                next_seq = str(year) + '/' + next_seq
            if self.faculty_id:
                pass
            else:
                self._cr.execute("""select count(*) as counter from ems_enrollment where student_id = %s and type='I'"""%(self.enrollment_id.student_id.id))
                result = self._cr.fetchone()
                if result:
                    result = result[0]
                    if result < 1:
                        raise UserError(_('The student does not have any inscription enrollments yet.'))
            self.write({'state':'validate', 'sequence':next_seq, 'year':str(year), 'number':str_number, 'processor_id':self._uid})

    @api.multi
    def action_pending(self):
        return self.write({'state':'pending'})

    @api.multi
    def action_deliver(self):
        return self.write({'state':'done'})

    @api.multi
    def action_print(self):

        #self.write({'state':'done'})
        #attach report in Students Attachments:
        inscription_subject_id=0
        edition_id=0
        subject_id=0
        str_course=''
        semester = 0
        year = 0.0
        year_str = ''
        if self.request_type_id.is_grade:
            enrollments = self.env['ems.enrollment'].search([('student_id','=',self.enrollment_id.student_id.id),('type','=','I')], order="course_year")
            for enrollment in enrollments:
                count=0
                enrollment_id=enrollment.id
                inscription_subjects = self.env['ems.enrollment.inscription.subject'].search([('inscription_id','=',enrollment_id)], order="course_year,semester_copy,id")
                for subject in inscription_subjects:
                    inscription_subject_id=subject.id
                    subject_id=subject.subject_id.id
                    edition_id=subject.edition_id.id
                    if count==0:
                        insc_subject = self.env['ems.enrollment.inscription.subject'].browse(inscription_subject_id)
                        if subject.course_year !='0':
                            print "ENTROU NO IF::::::::::::::::::::::::::::::::::"
                            insc_subject.write({'course_report': subject.course_year})
                        else:
                            print "ENTROU NO ELSE::::::::::::::::::::::::::::::::::"
                            ems_edition_subject_id = self.env['ems.edition.subject'].search([('subject_id','=',subject_id),('edition_id','=',edition_id)])
                            if ems_edition_subject_id:
                                print "ENTROU NO IF:::::::::::::::::::::::::::::::::::::::"
                                semester = int(ems_edition_subject_id.semester)
                                print semester
                                if semester > 0:
                                    year = semester / (2 * 1.0)
                                    year = math.ceil(year)
                                year_str = str(int(year))
                                print "YEAR STR:::::::::::::::::::::::::::::::::::::"
                                print year_str
                                insc_subject.write({'course_report': year_str})                           
                    else:
                        insc_subject = self.env['ems.enrollment.inscription.subject'].browse(inscription_subject_id)
                        insc_subject.write({'course_report': ''})
                    count = count + 1

        report = self.env['report'].get_pdf(self, self.request_type_id.report_id.report_name)
        result = base64.b64encode(report)
        file_name = str(self.request_type_id.name.encode('utf-8')) + '.pdf'
        self.env['ir.attachment'].create({
									'name': file_name, 
									'datas': result, 
									'datas_fname': file_name, 
									'res_model': 'ems.student',
									'res_id': self.enrollment_id.student_id.id,
									'type': 'binary'
								})
        return self.env['report'].get_action(self, self.request_type_id.report_id.report_name)

    @api.multi
    def action_draft(self):
        return self.write({'state':'draft'})

    @api.onchange('enrollment_id')
    def onchange_enrollment(self):
        student_name = ''
        enrollment_id = self.enrollment_id.id
        enrollments = self.env['ems.enrollment'].search([('id','=',enrollment_id)])
        for enrollment in enrollments:
            student_name=enrollment.student_id.complete_name
        self.name = student_name

    @api.onchange('faculty_id')
    def onchange_faculty(self):
        faculty_name = ''
        faculty_id = self.faculty_id.id
        faculties = self.env['ems.faculty'].search([('id','=',faculty_id)])
        for faculty in faculties:
            faculty_name=faculty.complete_name
        self.name = faculty_name
		
    def get_academic_year(self, student_id):
        if student_id:
            academic_year = 0
            academic_year2 = 0
            str_academic_year=''
            enrollments = self.env['ems.enrollment'].search([('student_id','=',student_id),('type','=','I')], order="id desc", limit=1)
            for enrollment in enrollments:
                academic_year=enrollment.academic_year
                academic_year2 = int(academic_year) + 1
                str_academic_year = str(academic_year) + '/' + str(academic_year2)
            return str_academic_year
        return None

    def get_course_year(self, student_id):
        if student_id:
            course_year = 0
            enrollments = self.env['ems.enrollment'].search([('student_id','=',student_id),('type','=','I')], order="id desc", limit=1)
            for enrollment in enrollments:
                course_year=enrollment.course_year
            return course_year
        return None

    def get_curr_inscription_academic_year(self, student_id):
        if student_id:
            academic_year = ''
            academic_year2 = 0
            str_academic_year=''
            count = 0
            enrollments = self.env['ems.enrollment'].search([('student_id','=',student_id),('type','=','I')])
            for enrollment in enrollments:
                try:
                    if count == 0:
                        academic_year = enrollment.academic_year
                        academic_year2 = int(academic_year) + 1
                        str_academic_year = str(academic_year) + '/' + str(academic_year2)

                        start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                        count = count + 1
                    else:
                        if start_date <= datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date() and enrollment.type=='I':
                            start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                            academic_year = enrollment.academic_year
                            academic_year2 = int(academic_year) + 1
                            str_academic_year = str(academic_year) + '/' + str(academic_year2)
                except Exception:
                    pass

        return str_academic_year

    def get_curr_inscription_course_year(self, student_id):
        if student_id:
            course_year = ''
            count = 0
            enrollments = self.env['ems.enrollment'].search([('student_id','=',student_id),('type','=','I')])
            for enrollment in enrollments:
                try:
                    if count == 0:
                        course_year = enrollment.course_year

                        start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                        count = count + 1
                    else:
                        if start_date <= datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date() and enrollment.type=='I':
                            start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                            course_year = enrollment.course_year
                except Exception:
                    pass

        return course_year
		
    def get_year(self, year):
        academic_year=0
        academic_year2=0
        str_academic_year=''
        if year:
            academic_year = year
            academic_year2 = int(academic_year) + 1
            str_academic_year = str(academic_year) + '/' + str(academic_year2)
        return str_academic_year
