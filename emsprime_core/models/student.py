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
    @api.depends('birth_date')
    def _get_age(self):
        today = date.today()
        if self.birth_date:
            birth_date = datetime.strptime(self.birth_date, '%Y-%m-%d').date()
            self.age = str(today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day)))

    @api.one
    @api.depends('birth_date')
    def _get_birth_year(self):
        birth_date = datetime.strptime(self.birth_date, '%Y-%m-%d').date()
        self.birth_year = str(birth_date.year)

    @api.one
    @api.depends('roll_number_line')
    def _get_curr_enrollment(self):
        roll_number = ''
        course_id = False
        edition_id = False
        type_current_enroll = ''
        transferred = False
        course_completed = False
        university_center_id = False
        #check current date with the latest enrollment edition:
        count = 0
        for enrollment in self.roll_number_line:
            try:
                if count == 0:
                    edition_id = enrollment.edition_id.id
                    course_id = enrollment.course_id.id
                    roll_number = enrollment.roll_number
                    type_current_enroll = enrollment.type
                    university_center_id = enrollment.university_center_id.id

                    start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                    count = count + 1
                else:
                    if start_date <= datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date() and enrollment.type=='M':
                        start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                        edition_id = enrollment.edition_id.id
                        course_id = enrollment.course_id.id
                        roll_number = enrollment.roll_number
                        type_current_enroll = enrollment.type
                        university_center_id = enrollment.university_center_id.id
                if type_current_enroll=='C':
                    type_current_enroll='Candidatura'
                else:
                    type_current_enroll='Matricula'
            except Exception:
                pass

            if enrollment.type == 'T':
                transferred = True

            if enrollment.type == 'CC':
                course_completed = True

        self.roll_number = roll_number
        self.edition_id = edition_id
        self.course_id = course_id
        self.type_current_enroll = type_current_enroll
        self.university_center_id = university_center_id
        self.transferred = transferred
        self.course_completed = course_completed

    active = fields.Boolean('Is Active?', default=True)
    middle_name = fields.Char('Middle Name', size=128, track_visibility='onchange')
    last_name = fields.Char('Last Name', size=128, required=True, track_visibility='onchange')
    birth_date = fields.Date('Birth Date', required=False, track_visibility='onchange')
    blood_group = fields.Selection(
        [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'), ('AB+', 'AB+ve'),
         ('A-', 'A-ve'), ('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],
        'Blood Group', track_visibility='onchange')
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female'),
         ('o', 'Other')], 'Gender', required=True, track_visibility='onchange')
    nationality = fields.Many2one('ems.location', 'Nationality', track_visibility='onchange')
    emergency_contact = fields.Many2one(
        'res.partner', 'Emergency Contact', track_visibility='onchange')
    visa_info = fields.Char('Visa Info', size=64, track_visibility='onchange')
    id_number = fields.Char('ID Card Number', size=64, track_visibility='onchange')
    passport_no = fields.Char('Passport/BI', size=20, track_visibility='onchange')
    photo = fields.Binary('Photo', track_visibility='onchange')
    lang = fields.Selection(_lang_get, 'Language', default='pt_PT', track_visibility='onchange')
    course_ids = fields.Many2many('ems.course', 'ems_student_course_rel', 'student_id', 'course_id', 'Course(s)', track_visibility='onchange')
    #edition_id = fields.Many2one('ems.edition', 'Edition', required=False)
    roll_number_line = fields.One2many(
        'ems.enrollment', 'student_id', 'Roll Number', track_visibility='onchange')
    partner_id = fields.Many2one(
        'res.partner', 'Partner', required=True, ondelete="cascade", track_visibility='onchange')

    roll_number = fields.Char(string='Current Roll Number', compute='_get_curr_enrollment', store=True, track_visibility='onchange')
    course_id = fields.Many2one('ems.course', string='Course', compute='_get_curr_enrollment', store=True, track_visibility='onchange')
    edition_id = fields.Many2one('ems.edition', string='Edition', compute='_get_curr_enrollment', store=True, track_visibility='onchange')
    user_id = fields.Many2one('res.users', 'Related User')

    gr_no = fields.Char("GR Number", size=20, track_visibility='onchange')
    location_id = fields.Many2one('ems.location', 'Place of birth', track_visibility='onchange')
    mother = fields.Char('Mother', size=255, track_visibility='onchange')
    father = fields.Char('Father', size=255, track_visibility='onchange')
    issuer = fields.Char('Issuer', track_visibility='onchange')
    issue_date = fields.Date('Issue Date', track_visibility='onchange')
    institutional_email = fields.Char('Institutional email', size=128, track_visibility='onchange')
    complete_name = fields.Char('Name', compute='_get_complete_name', store=True, track_visibility='onchange')
    attachment_line = fields.One2many('ems.attachment', 'student_id', 'Attachments')
    country_id = fields.Many2one('ems.location', 'Country', track_visibility='onchange')
    island_id = fields.Many2one('ems.location', 'Island', track_visibility='onchange')
    county_id = fields.Many2one('ems.location', 'County', track_visibility='onchange')
    parish_id = fields.Many2one('ems.location', 'Parish', track_visibility='onchange')
    #app_course_year = fields.Char("Course/Year", size=255)
    app_course_year = fields.Selection(
        [('8 ano', '8º ano'), ('9 ano', '9º ano'),('10 ano', '10º ano'),('11 ano', '11º ano'),('12 ano', '12º ano'),
         ('Bacharelato', 'Bacharelato'),('Licenciatura', 'Licenciatura'),('Pós-graduação', 'Pós-graduação'),('Mestrado', 'Mestrado'),('Doutoramento', 'Doutoramento')],
        'Course/Year', track_visibility='onchange')		
    app_course_academic_year = fields.Char("Academic Year", size=64, track_visibility='onchange')
    app_course_area = fields.Char("Area", size=255, track_visibility='onchange')
    math_final_average = fields.Float('Math Final Average', digits=(8,0), track_visibility='onchange')
    course_option_1 = fields.Many2one('ems.course', 'Course - Option 1', track_visibility='onchange')
    course_option_2 = fields.Many2one('ems.course', 'Course - Option 2', track_visibility='onchange')
    course_option_3 = fields.Many2one('ems.course', 'Course - Option 3', track_visibility='onchange')
    high_school_score = fields.Char('High School', track_visibility='onchange')
    schedule_choice = fields.Selection(
        [('morning', 'Morning'), ('afternoon', 'Afternoon'),
         ('evening', 'Evening')],
        'Schedule Choice', default="morning", track_visibility='onchange')
    sponsorship = fields.Selection(
        [('own_expenses', 'Own Expenses'), ('scholarship', 'Scholarship'),
         ('company', 'Company')],
        'Sponsorship', default="own_expenses", track_visibility='onchange')		
    state = fields.Selection([('draft', 'New'),
                              ('submit', 'Submitted'),
                              ('received', 'Received'),
                              ('confirmed', 'Accepted'),
                              ('rejected', 'Rejected')], 'State', default='draft', track_visibility='onchange',translate=False)
    #Permanant Address fields:
    pstreet = fields.Char('Street', track_visibility='onchange')
    pstreet2 = fields.Char('Street2', track_visibility='onchange')
    pcity = fields.Char('City', track_visibility='onchange')
    pzip = fields.Char('PostCode', track_visibility='onchange')
    acountry_id = fields.Many2one('ems.location', 'Country', track_visibility='onchange')
    pcountry_id = fields.Many2one('ems.location', 'Country', track_visibility='onchange')
    portuguese_final_average = fields.Float('Average Portuguese', digits=(8,0), track_visibility='onchange')
    final_average = fields.Float('Final Average', track_visibility='onchange')
    university_center_id = fields.Many2one('ems.university.center', 'University Center', track_visibility='onchange')
    type_current_enroll = fields.Char(string='Type of current enrollment', compute='_get_curr_enrollment', store=True, track_visibility='onchange')
    temp_edition_courses = fields.Many2many('ems.course', string='Course(s)')

    #JCF - Professional Contacts:
    pro_phone = fields.Char('Phone', track_visibility='onchange')
    pro_mobile = fields.Char('Mobile', track_visibility='onchange')
    pro_email = fields.Char('Email', track_visibility='onchange')

    scholarship_ids = fields.One2many('ems.scholarship', 'student_id', 'Scholarships')
    #JCF - Add type of document
    document_type = fields.Selection(
        [('idCard', 'ID Card'), ('passport', 'Passport')],
        'Document type', default="idCard", track_visibility='onchange')

    birth_year = fields.Char(string='Birth Year', compute='_get_birth_year', store=True, track_visibility='onchange')
    age = fields.Char(string='Age', compute='_get_age', store=True, track_visibility='onchange')
    transferred = fields.Boolean(compute="_get_curr_enrollment", string="Transferred", store=True)
    course_completed = fields.Boolean(compute="_get_curr_enrollment", string="Course Completed", store=True)

    @api.one
    @api.constrains('birth_date')
    def _check_birthdate(self):
        if self.birth_date and datetime.strptime(self.birth_date, '%Y-%m-%d').date() > datetime.now().date():
            raise ValidationError(
                "Birth Date can't be greater than current date!")

    @api.onchange('country_id')
    def _onchange_country(self):
        self.island_id = False
        self.county_id = False
        self.parish_id = False

    @api.onchange('university_center_id')
    def onchange_university_center(self):
        university_center_id = self.university_center_id.id
        editions = self.env['ems.edition'].search([('university_center_id','=',university_center_id)])
        courses = []
        for edition in editions:
            courses.append(edition.course_id.id)
        self.temp_edition_courses = [[6, 0, courses]]
        self.course_option_1 = False
        self.course_option_2 = False
        self.course_option_3 = False

    @api.multi
    @api.depends('name', 'roll_number')
    def name_get(self):
        result = []
        for student in self:
            rollno = student.roll_number and str(student.roll_number) + ' - ' or ''
            name = rollno + '' + student.name + ' ' + student.last_name
            result.append((student.id, name))
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Dynamically format University Center Filters On Student search view
        """
        res = super(EmsStudent, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        '''if view_type == 'form':
            """Filter Course Options list to show courses from Editions where edition Start Date 
            is greater than Todays Date.
            """
            today = fields.Date.today()
            editions = self.env['ems.edition'].search([('start_date','>',today)])
            courses = []
            course_list = [courses.append(edition.course_id.id) for edition in editions]
            if courses:
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//field[@name='course_option_1']"):
                    node.set('domain', "[('id','in',%s)]"%(courses))
                    node.set('widget', 'selection')
                    res['arch'] = etree.tostring(doc)
                for node in doc.xpath("//field[@name='course_option_2']"):
                    node.set('domain', "[('id','in',%s)]"%(courses))
                    node.set('widget', 'selection')
                    res['arch'] = etree.tostring(doc)
                for node in doc.xpath("//field[@name='course_option_3']"):
                    node.set('domain', "[('id','in',%s)]"%(courses))
                    node.set('widget', 'selection')
                    res['arch'] = etree.tostring(doc)'''
        if view_type == 'search':
            center_ids = self.env['ems.university.center'].search([('id','>',0)])
            centers, center_ref = [], []
            if center_ids:
                for center in center_ids:
                    centers.append(center.name)
                    center_ref.append(center.id)
                for r in range(0, len(centers)):
                    doc = etree.XML(res['arch'])
                    sfilter = etree.Element('filter')
                    sfilter.set('string', centers[r])
                    sfilter.set('domain', "[('university_center_id','=',%s)]"%(center_ref[r]))
                    node = doc.xpath("//field[@name='institutional_email']")
                    node[0].addnext(sfilter)
                    res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        user = context.get('uid', False)
        imd = self.env['ir.model.data']
        student_access_groups = ['emsprime_core.group_ems_faculty', 
                                 'emsprime_core.group_ems_back_office', 
                                 'emsprime_core.group_ems_back_office_admin','emsprime_core.group_ems_admin_sga' ]
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
            year = datetime.now().date().year
            university_center_id = student.university_center_id and student.university_center_id.id or False
            editions = self.env['ems.edition'].search([('course_id','=',course_id), 
                                                       ('university_center_id','=',university_center_id),
                                                       ])
            edition_id = False
            for edition in editions:
               edition_start_year = datetime.strptime(edition.start_date, "%Y-%m-%d").year
               if edition_start_year == year:
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

    @api.multi
    def open_inscriptions(self):
        for student in self:
            inscription_ids = self.env['ems.enrollment'].search([('student_id','=',student.id), ('type','=','I')])
            inscriptions = []
            inscription_list = [inscriptions.append(insc.id) for insc in inscription_ids]
            action = self.env.ref('emsprime_core.act_open_ems_inscription_enrollment_view')
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'view_type': action.view_type,
                'view_mode': action.view_mode,
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
            }
            tree = self.env.ref('emsprime_core.view_ems_enrollment_tree', False)
            tree_id = tree.id if tree else False
            form = self.env.ref('emsprime_core.view_ems_enrollment_inscription_student_form', False)
            form_id = form.id if form else False
            result['views'] = [(tree_id, 'tree'), (form_id, 'form')]
            result['domain'] = "[('id','in',["+','.join(map(str, inscriptions))+"])]"
            result['context'] = {'default_type': 'I', 'default_student_id': student.id}
        return result

    @api.multi
    def update_inscription_course_year(self):
        """ Temporary function to Update Student Inscription's Course Year
        """
        inscriptions = self.env['ems.enrollment'].search([('type', '=', 'I')], order="student_id, roll_number")
        student_course_list = []
        for inscription in inscriptions:
            student_course = [inscription.student_id.id, inscription.course_id.id]
            if student_course not in student_course_list:
                student_course_list.append(student_course)
                course_year = 1
            else:
                course_year += 1
            if not inscription.course_year:
                inscription.write({'course_year': str(course_year)})

    @api.multi
    def report_student_course_plan_data(self, var=False):
        for student in self:
            matricula_id = self.env['ems.enrollment'].search([('student_id','=',student.id), ('type','=','M')], limit=1)
            course = student.course_id
            if var == 'degree':
                return course.degree_id.name or ''
            if var == 'course':
                return course.name
            if var == 'university_center_id':
                return matricula_id.university_center_id.name
            if var == 'academic_year':
                return matricula_id.academic_year

    @api.multi
    def report_student_course_plan_subjects(self, semester_ids=False):
        enrollment_id = self.env['ems.enrollment'].search([('student_id','=',self.id), ('type','=','M')], limit=1)
        temp_course_plans = self.env['ems.course.plan'].search([('course_id','=',self.course_id.id)])
        student_course_plans = []
        for cpl in temp_course_plans:
            student_course_plans.append(cpl.id)
        sem_ids, semesters, subjects = [], [], []
        course_plan = []
        if enrollment_id:
            if semester_ids:
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
            for subj in subjects:
                #check if this subject exists in student inscription subjects list :
                student_inscriptions = self.env['ems.enrollment'].search([('student_id', '=', self.id)])
                student_inscriptions2 = []
                for stdi in student_inscriptions:
                    student_inscriptions2.append(stdi.id)
                inscription_subject_check = self.env['ems.enrollment.inscription.subject'].search([('inscription_id', 'in', student_inscriptions2), 
                										('subject_id','=',subj)])
                if inscription_subject_check:
                    for inscription in enrollment_id.student_id.roll_number_line:
                        flag = False
                        if inscription.type == 'I':
                            for line in inscription.subject_line:
                                lines = {}
                                if line.subject_id.id == subj:
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

                                    lines['subject_name'] = line.subject_id.name
                                    lines['grade'] = line.grade
                                    if line.grade:
                                        if line.grade > 9:
                                            lines['result'] = 'approved'
                                        else:
                                            lines['result'] = 'failed'
                                    else:
                                        lines['result'] = False
                                    if not line.grade:
                                        lines['grade'] = False
                                    result.append(lines)
                                    flag = True
                                    break
                        if flag:
                            break
                else:
                    course_plan_subject_ids = self.env['ems.course.plan.subject'].search([('course_plan_id','in',student_course_plans), ('subject_id','=',subj)], limit=1)
                    lines = {}
                    lines['course_year'] = ''
                    csemester = ''
                    if course_plan_subject_ids.semester in ('1', '3', '5', '7'):
                        csemester = '1º Semestre'
                    elif course_plan_subject_ids.semester in ('2', '4', '6', '8'):
                        csemester = '2º Semestre'
                    lines['grade_semester'] = csemester
                    lines['grade'] = ''
                    lines['subject_name'] = course_plan_subject_ids.subject_id.name
                    lines['result'] = False
                    result.append(lines)
        return result



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
