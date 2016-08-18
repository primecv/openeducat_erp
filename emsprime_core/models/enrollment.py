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
from datetime import datetime
from openerp.exceptions import ValidationError, UserError

class EmsEnrollment(models.Model):
    _name = 'ems.enrollment'
    _rec_name = 'roll_number'

    @api.one
    @api.depends('edition_id')
    def _get_year(self):
        year = datetime.strptime(self.edition_id.start_date, '%Y-%m-%d').date().year
        self.year = year

    roll_number = fields.Char('Roll Number', size=15, required=True)
    course_id = fields.Many2one('ems.course', 'Course', required=True)
    edition_id = fields.Many2one('ems.edition', 'Edition', required=True)
    student_id = fields.Many2one('ems.student', 'Student', required=True)
    student_roll_number = fields.Char(related='student_id.roll_number', string='Roll number', store=False)
    first_name = fields.Char(related='student_id.name', string='Name', store=False)
    middle_name = fields.Char(related='student_id.middle_name', string='Middle Name', store=False)
    last_name = fields.Char(related='student_id.last_name', string='Last Name', store=False)
    photo = fields.Binary(related='student_id.photo', string='Photo', store=False)
    state = fields.Selection([('draft','New'),('validate','Validated')], string='State', default='draft')
    academic_year = fields.Char('Academic Year', size=4, track_visibility='onchange')
    subject_ids = fields.Many2many('ems.subject', 'ems_enrollment_subjects_rel', 'enrollment_id', 'subject_id', 'Subjects')
    subject_ids_copy = fields.Many2many('ems.subject', 'ems_enrollment_subjects_copy_rel', 'enrollment_id', 'subject_id', 'Subjects')
    subject_line = fields.One2many('ems.enrollment.inscription.subject', 'inscription_id', 'Subjects')
    type = fields.Selection(
        [ ('C', 'Candidatura'), ('I', 'Inscrição'), ('M', 'Matricula')], 'Tipo', required=True, default='M')
    period = fields.Selection([('morning','Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')], 'Period')
    university_center_id = fields.Many2one('ems.university.center', related="edition_id.university_center_id", string='University Center', store=True)
    year = fields.Char(string='Year', compute='_get_year', store=True)
    course_year = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], 'Course Year',
                     track_visibility='onchange')

    def get_to_year(self, year):
        if year:
           return int(year) + 1
        return None

    @api.onchange('student_id', 'course_id', 'edition_id', 'academic_year', 'type')
    def onchange_enrollment_data(self):
        if self.type == 'I':
            if self.student_id and self.student_id.course_id:
                subjects = []
                subject_list = [subjects.append(subject.subject_id.id) for subject in self.course_id.subject_line]
                self.update({
                    'edition_id': self.student_id.edition_id.id,
                    'course_id': self.student_id.course_id.id,
                    'subject_ids_copy': [[6,0,subjects]]
                })
            else:
               self.update({'edition_id': False, 'course_id': False, 'subject_ids_copy':[[6,0,[]]]})

    @api.onchange('course_id')
    def onchange_course(self):
        self.update({'edition_id': False})
        if not self.course_id:
            self.update({'subject_ids_copy':[[6,0,[]]]})
        else:
            subjects = []
            subject_list = [subjects.append(subject.subject_id.id) for subject in self.course_id.subject_line]
            self.update({'subject_ids_copy': [[6,0,subjects]]})

    @api.constrains('type', 'student_id')
    def check_inscricao_enrollment(self):
        for enrollment in self:
            if enrollment.type == 'I':
                student = enrollment.student_id.id
                matriculas = self.search([('student_id','=',student), ('type','=','M')])
                if not matriculas:
                    raise ValidationError(_('Inscrição enrollment cannot be created.\nStudent must be enrolled with Matricula type.'))
        return True

    _sql_constraints = [
        ('unique_name_roll_number_id',
         'unique(roll_number,course_id,edition_id,student_id)',
         'Roll Number & Student must be unique per Edition!'),
        ('unique_name_roll_number_course_id',
         'unique(roll_number,course_id,edition_id)',
         'Roll Number must be unique per Edition!'),
        ('unique_roll_number', 'unique(roll_number)', 'Student Already Exists with Roll Number.')
    ]

    @api.model
    def create(self, vals):
        context = self._context
        #set Type|Edition|Course from context as they are readonly on Inscription form:
        if context and dict(context): 
            if 'default_type' in context and 'type' not in vals:
                vals['type'] = context['default_type']
            if 'default_student_id' in context:
                vals['student_id'] = context['default_student_id']
                student = self.env['ems.student'].browse([context['default_student_id']])
                if 'edition_id' not in vals:
                    vals['edition_id'] = student.edition_id.id
                if 'course_id' not in vals:
                    vals['course_id'] = student.course_id.id

                current_year = datetime.now().date().year
                edition_start_year = datetime.strptime(student.edition_id.start_date, '%Y-%m-%d').year
                edition_end_year = datetime.strptime(student.edition_id.end_date, '%Y-%m-%d').year
                if edition_end_year > current_year:
                    edition_end_year = current_year
                edition_years = []
                diff = edition_end_year - edition_start_year
                for y in range(0, diff+1):
                    edition_years.append(edition_start_year + y)
                inscription_years = []
                inscriptions = self.env['ems.enrollment'].search([('type','=','I'),('student_id','=',student.id)])
                for inscription in inscriptions:
                    inscription_years.append(inscription.academic_year)
                valid_years = []
                for y in edition_years:
                    if str(y) not in inscription_years:
                        valid_years.append(str(y))
                if not valid_years:
                    raise UserError(_('Inscription Enrollments are already present for all valid Academic Years.'))
                else:
                    if vals['academic_year'] not in valid_years:
                        valid_years = [' | '.join(valid_years)][0]
                        raise UserError(_('Invalid Academic Year!\nValid Academic Years: %s')%(valid_years))
        if 'type' in vals and vals['type'] == 'C':
            last_rec = self.search([('id','>',0),('roll_number','!=', ''),('type','=','C')], order='id desc', limit=1)
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
        elif 'type' in vals and vals['type'] == 'I' and 'no_rollno' not in self._context:
            student_roll_no = self.env['ems.student'].browse([vals['student_id']]).roll_number
            vals['roll_number'] = str(student_roll_no) + '.' + str(vals['academic_year'])
        return super(EmsEnrollment, self).create(vals)

    @api.multi
    def action_load_subjects(self):
        """Load related Course - Semester Subjects in Inscription Enrollments
        """
        for enrollment in self:
            if enrollment.course_year:
                year = int(enrollment.course_year)
                sem1, sem2 = (year*2)-1, year*2
                subjects, invalid_subjects = [], []
                #subjects_list = [subjects.append(s.subject_id.id) for s in enrollment.subject_line]
                #get existing inscription subjects :
                inscriptions = self.env['ems.enrollment'].search([('type','=','I'),('student_id','=',enrollment.student_id.id)])
                for insc in inscriptions:
                    for subj_line in insc.subject_line:
                        if subj_line.semester in (sem1, sem2) and subj_line.grade >= 10:
                            subjects.append(subj_line.subject_id.id)
                sem_subject_ids = self.env['ems.edition.subject'].search([('edition_id','=',enrollment.edition_id.id),('semester','in',(str(sem1), str(sem2)))])
                for sem_subject in sem_subject_ids:
                    if sem_subject.subject_id.id not in subjects:
                        self.env['ems.enrollment.inscription.subject'].create({
                                'inscription_id': enrollment.id,
                                'subject_id': sem_subject.subject_id.id,
                                'semester': sem_subject.subject_id.semester or sem_subject.semester
                        })
                invalid_subjects = self.env['ems.enrollment.inscription.subject'].search([
                                        ('inscription_id','=',enrollment.id),   
                                        ('semester','not in', (str(sem1),str(sem2))) ])
                for line in invalid_subjects:
                    line.unlink()            
                        
    @api.one
    def action_validate(self):
        return self.write({'state': 'validate'})
            

class EmsEnrollmentInscriptionSubject(models.Model):
    _name = "ems.enrollment.inscription.subject"
    _description = "Grades"
    _order = "semester asc"

    @api.onchange('subject_id', 'semester', 'ect')
    def onchange_subject(self):
        context = self._context
        vals = {}
        subject_id = self.subject_id.id
        if context and 'edition_id' in context:
            edition_id = context['edition_id']
            ems_edition_subject_id = self.env['ems.edition.subject'].search([('subject_id','=',subject_id),('edition_id','=',edition_id)])
            if ems_edition_subject_id:
                vals['semester'] = ems_edition_subject_id.semester
                vals['ect'] = ems_edition_subject_id.ects
                vals['semester_copy'] = ems_edition_subject_id.semester
                vals['ect_copy'] = ems_edition_subject_id.ects
        else:
            vals['semester'] = self.semester_copy
            vals['ect'] = self.ect_copy
        self.update(vals)

    inscription_id = fields.Many2one('ems.enrollment', 'Inscription')
    course_id = fields.Many2one('ems.course', related='inscription_id.course_id', string='Course', store=True)
    edition_id = fields.Many2one('ems.edition', related='inscription_id.edition_id', string='Edition', store=True)
    student_id = fields.Many2one('ems.student', related='inscription_id.student_id', string='Student', store=True)
    subject_id = fields.Many2one('ems.subject', 'Subject')
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
    semester_copy = fields.Selection([('1', '1'), 
                                ('2', '2'), 
                                ('3', '3'),
                                ('4', '4'),
                                ('5', '5'),
                                ('6', '6'),
                                ('7', '7'),
                                ('8', '8'),
                                ('9', '9')
            ], 'Semester')
    ect = fields.Integer('ECT')
    ect_copy = fields.Integer('ECT')
    grade = fields.Integer('Grade', group_operator="avg")
    evaluation_type = fields.Selection([('exam', 'Exam'),('continuous', 'Continuous')], 'ET')
    period = fields.Selection([('morning','Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')], 'Period')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
