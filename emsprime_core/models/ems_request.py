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
from openerp.exceptions import ValidationError, UserError,QWebException
from lxml import etree
from openerp.osv.orm import setup_modifiers
	
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
    attachment_type = fields.Many2one('ems.attachment.type', 'Attachment type')
    grades_with_average = fields.Boolean('Grades with average?')
    approved = fields.Boolean('Approved?')

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
    @api.depends('processor_id')
    def _get_university_center(self):
        university_center_id = False
        users = self.env['res.users'].search([('id','=',self._uid)], order="id desc", limit=1)
        for user in users:
            university_center_id=user.university_center_id.id
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
    date = fields.Date('Request Date', track_visibility="onchange", default=datetime.now().date(), readonly=True)
    state = fields.Selection(
        [('draft', 'New Request'), ('validate', 'Processed'),
         ('pending', 'Pending'), ('done', 'Done')],
        'State', default="draft", required=True, track_visibility='onchange', select=True)
    sequence = fields.Char('Declaration Number')
    current_inscription_id = fields.Many2one('ems.enrollment', string='Current Inscription', compute='_get_curr_inscription', store=True, track_visibility='onchange')
    university_center_id = fields.Many2one('ems.university.center', string='University Center', compute='_get_university_center', store=True, track_visibility='onchange')
    year = fields.Char('Year of Declaration')
    number = fields.Char('Number of Declaration')
    report_type = fields.Selection(
        [('S', 'Student'), ('F', 'Faculty')], 'Type',related='request_type_id.type', track_visibility='onchange', store=True)
    faculty_id = fields.Many2one('ems.faculty', 'Faculty', track_visibility='onchange')
    regime = fields.Selection(
        [('24h', '24 horas'), ('48h', '48 horas'), ('72h', '72 horas'), ('normal', 'Normal'), ('GAS', 'Gabinete de Acção Social')], 'Regime', required=True, track_visibility='onchange')
    student_faculty = fields.Char(string='Student/Faculty', compute='_get_student_faculty', store=True)
    processor_id = fields.Many2one('res.users', 'Processor', track_visibility='onchange', select=True)
    report_type_grade = fields.Boolean('Report type grades?',related='request_type_id.is_grade', track_visibility='onchange', store=False)
    course_year = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),('all','All')], 'Year', track_visibility='onchange')
    semester_id = fields.Many2one('ems.request.semester', 'Semester', track_visibility='onchange')
    semester_ids = fields.Many2many('ems.request.semester', 'ems_request_semester_rel', 'request_id', 'semester_id', 'Semester(s)', track_visibility='onchange')
    report_signature = fields.Char('Signature')
    issue_date = fields.Date('Issue Date', track_visibility='onchange')

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

    @api.multi
    def write(self, vals):
        """ Restrict user other than Back office admins to modify Requests not belonging to their related University Center.
        """
        uid = self._uid
        backoffice_admin_groupid = self.env['ir.model.data'].xmlid_to_res_id('emsprime_core.group_ems_back_office_admin')
        if backoffice_admin_groupid and uid:
            self._cr.execute("select uid from res_groups_users_rel where gid=%s and uid=%s"%(backoffice_admin_groupid, uid))
            result = False
            try:
                result = self._cr.fetchone()[0]
            except Exception:
                pass
            if not result: #user do not have back office admin access
                user = self.env['res.users'].browse([uid])
                university_center_id = user.university_center_id and user.university_center_id.id or False
                if university_center_id:
                    if self.report_type == 'S':
                        student_univ_center = self.enrollment_id.student_id.university_center_id and self.enrollment_id.student_id.university_center_id.id or False
                        if university_center_id != student_univ_center:
                            raise UserError(_('User do not have permission to modify this document.\n\nPlease contact your Administrator.'))
                    elif self.report_type == 'F':
                        faculty_univ_center = self.faculty_id.university_center_id and self.faculty_id.university_center_id.id or False
                        if faculty_univ_center != university_center_id:
                            raise UserError(_('User do not have permission to modify this document.\n\nPlease contact your Administrator.'))
                else:
                    raise UserError(_('User do not have permission to modify this document.\n\nPlease contact your Administrator.'))
        return super(ems_request, self).write(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """ This function makes Issue Date editable only to Back Office Admin group users.
        """
        res = super(ems_request, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        backoffice_admin_groupid = self.env['ir.model.data'].xmlid_to_res_id('emsprime_core.group_ems_back_office_admin')
        if view_type == 'form' and backoffice_admin_groupid:
            self._cr.execute("select uid from res_groups_users_rel where gid=%s and uid=%s"%(backoffice_admin_groupid, self._uid))
            result = False
            try:
                result = self._cr.fetchone()[0]
            except Exception:
                pass
            if result and result == self._uid:
                for node in doc.xpath("//field[@name='date']"):
                    node.set('readonly', '0')
                    setup_modifiers(node, res['fields']['date'])
                    res['arch'] = etree.tostring(doc)
            if not result:
                user = self.env['res.users'].browse([self._uid])
                university_center_id = user.university_center_id and user.university_center_id.id or False
                if university_center_id:
                    for node in doc.xpath("//field[@name='enrollment_id']"):
                        node.set('domain', "[('student_id.current_university_center_id', '=', %s), ('type', '=', 'M')]"%(university_center_id))
                        setup_modifiers(node, res['fields']['enrollment_id'])
                        res['arch'] = etree.tostring(doc)
                    for node in doc.xpath("//field[@name='faculty_id']"):
                        node.set('domain', "[('university_center_id', '=', %s)]"%(university_center_id))
                        setup_modifiers(node, res['fields']['faculty_id'])
                        res['arch'] = etree.tostring(doc)
        return res

    def get_to_year(self, year):
        if year:
           return int(year) + 1
        return None

    def get_semester(self, semester):
        semester_int=0
        if semester:
            semester_int=int(semester)
            if semester_int % 2 == 0:
                semester_int=2
            else:
                semester_int=1
            return semester_int
        return None

    def get_grade(self, subject_id):
        grade=''
        if subject_id:
            self._cr.execute("""select max(grade) as grade from ems_enrollment_inscription_subject where student_id=%s and subject_id=%s"""%(self.enrollment_id.student_id.id,subject_id))
            result = self._cr.fetchone()
            if result:
                result = result[0]
            if result==1:
                grade = "1 (Um) valor"
            elif result ==2:
                grade = "2 (Dois) valores"
            elif result ==3:
                grade = "3 (Três) valores"
            elif result ==4:
                grade = "4 (Quatro) valores"
            elif result ==5:
                grade = "5 (Cinco) valores"
            elif result ==6:
                grade = "6 (Seis) valores"
            elif result ==7:
                grade = "7 (Sete) valores"
            elif result ==8:
                grade = "8 (Oito) valores"
            elif result ==9:
                grade = "9 (Nove) valores"
            elif result ==10:
                grade = "10 (Dez) valores"
            elif result ==11:
                grade = "11 (Onze) valores"
            elif result ==12:
                grade = "12 (Doze) valores"
            elif result ==13:
                grade = "13 (Treze) valores"
            elif result ==14:
                grade = "14 (Quatorze) valores"
            elif result ==15:
                grade = "15 (Quinze) valores"
            elif result ==16:
                grade = "16 (Dezasseis) valores"
            elif result ==17:
                grade = "17 (Dezassete) valores"
            elif result ==18:
                grade = "18 (Dezoito) valores"
            elif result ==19:
                grade = "19 (Dezanove) valores"
            elif result ==20:
                grade = "20 (Vinte) valores"
            return grade
        return None

    @api.multi
    def action_validate(self):
        """Generate sequence in "YYYY/0001" format by University center
        """
        if not self.issue_date:
            self.write({'issue_date': datetime.now().date()})
        year = datetime.now().date().year
        next_seq = str(year) + '/0001'
        str_number = '0001'
        university_center_id, result = False, False
        users = self.env['res.users'].search([('id','=',self.create_uid.id)], order="id desc", limit=1)
        for user in users:
            university_center_id=user.university_center_id.id
        if self.sequence:
            self.write({'state':'validate'})
        else:
            if university_center_id:
                self._cr.execute("""select sequence from ems_request where university_center_id in (%s) and sequence ilike '%s%%' order by sequence desc limit 1"""%(university_center_id,str(year) + '/'))
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
                if self.request_type_id.type == 'S':
                    if self.enrollment_id:
                        self._cr.execute("""select count(*) as counter from ems_enrollment where student_id = %s and type='I'"""%(self.enrollment_id.student_id.id))
                        result = self._cr.fetchone()
                        if result:
                            result = result[0]
                            if result < 1:
                                raise UserError(_('The student does not have any inscription enrollments yet.'))
                    else:
                        raise ValidationError(_('Please Select Valid Enrollment.'))
            #if self.request_type_id.grades_with_average:
            #    valid = self.validate_grades(self.course_year)
            #    if valid == True:
            #        self.write({'state':'validate', 'sequence':next_seq, 'year':str(year), 'number':str_number, 'processor_id':self._uid})
            #    else:
            #        raise UserError(_('There are missing grades. The average cannot be calculated.'))
            #else:
            self.write({'state':'validate', 'sequence':next_seq, 'year':str(year), 'number':str_number, 'processor_id':self._uid})

    @api.multi
    def action_pending(self):
        return self.write({'state':'pending'})

    @api.multi
    def action_deliver(self):
        return self.write({'state':'done'})

    @api.multi
    def action_print(self):

        #attach report in Students Attachments:
        edition_subject_id=0
        str_course=''
        semester = 0
        year = 0.0
        year_int=0
        year_str = ''
        semester_str = ''
        if self.request_type_id.is_grade:
            course_plan_subjects = self.env['ems.course.plan.subject'].search([('course_plan_id','=',self.enrollment_id.edition_id.course_plan_id.id)], order="course_year,semester,ordering")
            count=0
            year_count=0
            semester_count=0
            for course_plan_subject in course_plan_subjects:
                course_plan_subject_id=course_plan_subject.id
                if count==0:
                    cp_subject = self.env['ems.course.plan.subject'].browse(course_plan_subject_id)
                    semester = int(course_plan_subject.semester)
                    if semester > 0:
                        year = semester / (2 * 1.0)
                        year = math.ceil(year)
                    year_int = int(year)
                    year_str = str(year_int)
                    if semester % 2 == 0:
                        semester=2
                    else:
                        semester=1
                    cp_subject.write({'course_report': year_str,'semester_report':'1'})
                    year_count=year_int
                    semester_count=semester
                else:
                    cp_subject = self.env['ems.course.plan.subject'].browse(course_plan_subject_id)
                    semester = int(course_plan_subject.semester)
                    if semester > 0:
                        year = semester / (2 * 1.0)
                        year = math.ceil(year)
                    year_int = int(year)
                    year_str = str(year_int)
                    if semester % 2 == 0:
                        semester=2
                    else:
                        semester=1
                    semester_str=str(semester)
                    if year_count == year_int:
                        cp_subject.write({'course_report': ''})
                    else:
                        cp_subject.write({'course_report': year_str})
                        year_count=year_int
                    if semester_count == semester:
                        cp_subject.write({'semester_report': ''})
                    else:
                        cp_subject.write({'semester_report': semester_str})
                        semester_count=semester
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
        self.env['ems.attachment'].create({
									'name': file_name, 
									'attachment': result, 
									'dates_fname': file_name, 
									'res_model': 'ems.student',
									'student_id': self.enrollment_id.student_id.id,
									'attachment_type_id': self.request_type_id.attachment_type.id,
									'type': 'binary'
								})
        return self.env['report'].get_action(self, self.request_type_id.report_id.report_name)

    @api.multi
    def action_draft(self):
        return self.write({'state':'draft'})

    @api.multi
    def get_subject_grades(self, enrollment_id=False, semester_ids=False):
        sem_ids, semesters, subjects = [], [], []
        course_plan = []
        if enrollment_id:
            for sem in semester_ids:
                sem_ids.append(sem.semester)
            for sem in sem_ids:
            	semesters.append(sem)
            	if sem in ('2', '4', '6', '8'):
            		sem1 = str(int(sem) -1)
            		semesters.append(sem1)
            #select all semesters if Semester(s) not selected:
            if not semester_ids:
                semester_ids = self.env['ems.request.semester'].search([('id', '>', 0)])
                temp = [semesters.append(s.semester) for s in semester_ids]

            matricula_subjects = []
            #get Matricula Enrollment course plan subjects:
            if enrollment_id.edition_id and enrollment_id.edition_id.course_plan_id and enrollment_id.edition_id.course_plan_id.subject_line:
                course_plan.append(enrollment_id.edition_id.course_plan_id.id)
                temp = [matricula_subjects.append(subject.subject_id.id) for subject in enrollment_id.edition_id.course_plan_id.subject_line 
                                                                                if subject.semester in semesters]
            #get inscription enrollment's course plan subjects:
            inscription_subjects = []
            for enrollment in enrollment_id.student_id.roll_number_line:
                if enrollment.type == 'I':
                    if enrollment.course_plan_id and enrollment.course_plan_id.subject_line:
                        course_plan.append(enrollment.course_plan_id.id)
                        temp = [inscription_subjects.append(subject.subject_id.id) for subject in enrollment.course_plan_id.subject_line
                                                                                      if subject.semester in semesters]
            #create final Subjects list:
            for subject in matricula_subjects:
                inscription_subjects.append(subject)
            temp = [subjects.append(subject) for subject in inscription_subjects if subject not in subjects]

            #ordering subjects list:
            subjects_list = self.env['ems.course.plan.subject'].search([('course_plan_id', 'in', course_plan), ('subject_id', 'in', subjects)], order="semester, ordering") 
            subjects = []
            temp = [subjects.append(subject.subject_id.id) for subject in subjects_list if subject.subject_id.id not in subjects]

            #get grades from student inscription based on subjects ordering:
            result = []
            course_year = ''
            grade_semester = ''
            grade = ''
            for subj in subjects:
                for inscription in enrollment_id.student_id.roll_number_line:
                    flag = False
                    if inscription.type == 'I':
                        for line in inscription.subject_line:
                            lines = {}
                            if line.subject_id.id == subj:
                                #find optional Course Plan Subject:
                                subject_optional = ''
                                inscription_course_plan = line.inscription_id.course_plan_id and line.inscription_id.course_plan_id.id or False
                                if not inscription_course_plan:
                                    inscription_course_plan = line.inscription_id.edition_id.course_plan_id and line.inscription_id.edition_id.course_plan_id.id or False
                                if inscription_course_plan:
                                    optional_course_plan_subject = self.env['ems.course.plan.subject'].search([('subject_id','=',line.subject_id.id), 
                                                                                                                ('course_plan_id','=',inscription_course_plan)])
                                    if optional_course_plan_subject and optional_course_plan_subject[0].optional is True:
                                        subject_optional = ' (Opcional)'

                                if not course_year:
                                    course_year = line.inscription_id.course_year
                                    lines['course_year'] = str(course_year) + 'º Ano'
                            	
                                if (line.inscription_id.course_year == course_year) and 'course_year' not in lines:
                                    lines['course_year'] = ''
                                else:
                                    course_year = line.inscription_id.course_year
                                    lines['course_year'] = str(course_year) + 'º Ano'

                                if not grade_semester:
                                    if line.semester in ('1', '3', '5', '7'):
                                        semester = '1º Semestre'
                                    elif line.semester in ('2', '4', '6', '8'):
                                        semester = '2º Semestre'
                                    grade_semester = line.semester
                                    lines['grade_semester'] = semester
                            	
                                if (line.semester == grade_semester) and 'grade_semester' not in lines:
                                    lines['grade_semester'] = ''
                                else:
                                    if line.semester in ('1', '3', '5', '7'):
                                        semester = '1º Semestre'
                                    elif line.semester in ('2', '4', '6', '8'):
                                        semester = '2º Semestre'
                                    grade_semester = line.semester
                                    lines['grade_semester'] = semester

                                #if line.
                                lines['subject_name'] = str(line.subject_id.name) + subject_optional
                                lines['grade'] = line.grade
                                if not line.grade:
                                	lines['grade'] = False
                                if line.grade==1:
                                    grade = "1 (Um) valor"
                                elif line.grade ==2:
                                    grade = "2 (Dois) valores"
                                elif line.grade ==3:
                                    grade = "3 (Três) valores"
                                elif line.grade ==4:
                                    grade = "4 (Quatro) valores"
                                elif line.grade ==5:
                                    grade = "5 (Cinco) valores"
                                elif line.grade ==6:
                                    grade = "6 (Seis) valores"
                                elif line.grade ==7:
                                    grade = "7 (Sete) valores"
                                elif line.grade ==8:
                                    grade = "8 (Oito) valores"
                                elif line.grade ==9:
                                    grade = "9 (Nove) valores"
                                elif line.grade ==10:
                                    grade = "10 (Dez) valores"
                                elif line.grade ==11:
                                    grade = "11 (Onze) valores"
                                elif line.grade ==12:
                                    grade = "12 (Doze) valores"
                                elif line.grade ==13:
                                    grade = "13 (Treze) valores"
                                elif line.grade ==14:
                                    grade = "14 (Quatorze) valores"
                                elif line.grade ==15:
                                    grade = "15 (Quinze) valores"
                                elif line.grade ==16:
                                    grade = "16 (Dezasseis) valores"
                                elif line.grade ==17:
                                    grade = "17 (Dezassete) valores"
                                elif line.grade ==18:
                                    grade = "18 (Dezoito) valores"
                                elif line.grade ==19:
                                    grade = "19 (Dezanove) valores"
                                elif line.grade ==20:
                                    grade = "20 (Vinte) valores"

                                lines['grade_print'] = grade
                                result.append(lines)
                                flag = True
                                break
                    if flag:
                        break
        return result
            

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

    def get_academic_year_by_year(self, course_year):
        if course_year:
            academic_year2 = 0
            str_academic_year=''
            enrollments = self.env['ems.enrollment'].search([('student_id','=',self.enrollment_id.student_id.id),('edition_id','=',self.enrollment_id.edition_id.id),('course_year','=',course_year)], order="id desc", limit=1)
            for enrollment in enrollments:
                academic_year=enrollment.academic_year
                academic_year2 = int(academic_year) + 1
                str_academic_year = str(academic_year) + '/' + str(academic_year2)
            return str_academic_year
        return None
		
    def get_average(self, course_year):
        if course_year:
            grades = 0
            count=0
            average=0.0
            str_average=''
            if course_year=='all':
                subjects_course_plan = self.env['ems.course.plan.subject'].search([('course_plan_id','=',self.enrollment_id.edition_id.course_plan_id.id)])
            else:
                subjects_course_plan = self.env['ems.course.plan.subject'].search([('course_plan_id','=',self.enrollment_id.edition_id.course_plan_id.id),('course_year','=',course_year)])
            for subject_course_plan in subjects_course_plan:
                subject_id=subject_course_plan.subject_id.id
                self._cr.execute("""select COALESCE( max(grade), '-1' ) as grade from ems_enrollment_inscription_subject where student_id=%s and subject_id=%s"""%(self.enrollment_id.student_id.id,subject_id))
                result = self._cr.fetchone()
                if result:
                    result = int(result[0])
                    if result > 0:
                        grades = grades + result
                        count = count + 1
            if count > 0:
                average = grades / (count * 1.0)
                average = math.ceil(average)
                str_average=str(int(average))
            return str_average
        return None

    def validate_grades(self, course_year):
        if course_year:
            course_year = 0
            if course_year=='all':
                self._cr.execute("""select count(*) as count from (select subject_id,grade from ems_enrollment_inscription_subject where student_id=%s) as v where v.grade is null"""%(self.enrollment_id.student_id.id))
            else:
                self._cr.execute("""select count(*) as count from (select subject_id,grade from ems_enrollment_inscription_subject where student_id=%s and course_year='%s') as v where v.grade is null"""%(self.enrollment_id.student_id.id,course_year))                
            result = self._cr.fetchone()
            if result:
                result = int(result[0])
                if result > 0:
                    return False
                else:
                    return True
        return None

    def check_semesters_request(self, semester):
        count=0
        if semester:
            self._cr.execute("""select count(*) as count from ems_request_semester_rel rel, ems_request_semester s where s.id=rel.semester_id and rel.request_id=%s and s.semester='%s'"""%(self.id))                
            result = self._cr.fetchone()
            if result:
                count = int(result[0])
                if count>0:
                    return True
                else:
                    return False
        return None
		
    def check_semester(self, semester):
        count=0
        semester_int=0
        semester_str=''
        if semester:
            semester_int=int(semester)
            semester_str=semester
            self._cr.execute("""select count(*) as count from ems_request_semester_rel rel, ems_request_semester s where s.id=rel.semester_id and rel.request_id=%s and s.semester='%s'"""%(self.id,semester_str))                
            result = self._cr.fetchone()
            if result:
                count = int(result[0])
                if count>0:
                    return True
                else:
                    if semester_int % 2 != 0:
                        semester_int = semester_int + 1
                        semester_str = str(semester_int)		
                        self._cr.execute("""select count(*) as count from ems_request_semester_rel rel, ems_request_semester s where s.id=rel.semester_id and rel.request_id=%s and s.semester='%s'"""%(self.id,semester_str))                
                        result = self._cr.fetchone()
                        if result:
                            count = int(result[0])
                            if count>0:
                                return True
                            else:
                                return False
                    else:
                        return False
        return None

		
class ems_request_semester(models.Model):
    _name = 'ems.request.semester'
    _description = "Request Semester"
    _order = 'name'
	
    name = fields.Char('Semester', required=True)
    semester = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),('6','6'),('7','7'),('8','8')], 'Semester', track_visibility='onchange')

		
