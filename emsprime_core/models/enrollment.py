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
import math
from openerp import models, fields, api, _
from datetime import datetime
from openerp.exceptions import ValidationError, UserError

class EmsEnrollment(models.Model):
    _name = 'ems.enrollment'
    _rec_name = 'roll_number'
    _order = 'enrollment_date'

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
    #academic_year = fields.Char('Academic Year', size=4, track_visibility='onchange')
    academic_year = fields.Selection([('2016', '2016/2017'),('2015', '2015/2016'), ('2014', '2014/2015'),('2013', '2013/2014'),('2012', '2012/2013'), 
                                      ('2011', '2011/2012'), ('2010', '2010/2011'), ('2009', '2009/2010'), ('2008', '2008/2009'), ('2007', '2007/2008'),
									  ('2006', '2006/2007'), ('2005', '2005/2006'), ('2004', '2004/2005'), ('2003', '2003/2004'),('2002', '2002/2003'),
									  ('2001', '2001/2002'),('2000', '2000/2001'),('1999', '1999/2000'),('1998', '1998/1999'),('1997', '1997/1998'),
									  ('1996', '1996/1997'), ('1995', '1995/1996'),('1994', '1994/1995'),('1993', '1993/1994'),('1992', '1992/1993'),
									  ('1991', '1991/1992')
            ], 'Academic Year', track_visibility='onchange')
    subject_ids = fields.Many2many('ems.subject', 'ems_enrollment_subjects_rel', 'enrollment_id', 'subject_id', 'Subjects')
    subject_ids_copy = fields.Many2many('ems.subject', 'ems_enrollment_subjects_copy_rel', 'enrollment_id', 'subject_id', 'Subjects')
    subject_line = fields.One2many('ems.enrollment.inscription.subject', 'inscription_id', 'Subjects')
    type = fields.Selection([ 
                                ('C', 'Candidatura'), 
                                ('I', 'Inscrição'), 
                                ('M', 'Matricula'), 
                                ('T', 'Transferência'), 
                                ('CC', 'Conclusão'), 
                                ('MC', 'Mudança de Curso')
                            ], 'Tipo', required=True, default='M')
    period = fields.Selection([('morning','Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')], 'Period')
    university_center_id = fields.Many2one('ems.university.center', related="edition_id.university_center_id", string='University Center', store=True)
    year = fields.Char(string='Year', compute='_get_year', store=True)
    course_year = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], 'Course Year',
                     track_visibility='onchange')
    student_status_id = fields.Many2one('ems.student.status', 'Student Status')
    course_plan_id = fields.Many2one('ems.course.plan', 'Course Plan')
    annulment = fields.Boolean('Annulment')
    annulment_date = fields.Date('Annulment Date')
    enrollment_date = fields.Date('Enrollment Date')
    course_conclusion_date = fields.Date('Conclusion Date')
    matricula_id = fields.Many2one('ems.enrollment', 'Matrícula')

    def get_to_year(self, year):
        if year:
           return int(year) + 1
        return None

    @api.model
    def default_get(self, fields):
        res = super(EmsEnrollment, self).default_get(fields)
        context = self._context
        if not context:
            context = {}
        if 'student_id' in context:
            student_id = context['student_id']
            student = self.env['ems.student'].browse(student_id)
            is_matricula = False
            student_course = False
            student_edition = False
            for std in student:
                for line in std.roll_number_line:
                    if line.type == 'M':
                        is_matricula = True
                    if line.type in ('T', 'M', 'MC'):
                        student_course = line.course_id.id
                        student_edition = line.edition_id.id
            if is_matricula is False:
                res.update(type = False)
            res.update(roll_number = student.roll_number)
            res.update(course_id = student_course)
            res.update(edition_id = student_edition)
        return res

    @api.onchange('type')
    def onchange_type(self):
        context = self._context
        if not context:
            context = {}
        if 'create_inscription' not in context:
            is_matricula = False
            if 'student_id' in context:
                student_id = context['student_id']
                student = self.env['ems.student'].browse([student_id])
                for line in student.roll_number_line:
                    if line.type == 'M':
                        is_matricula = True
            if (is_matricula is False and self.type in ('T', 'CC', 'MC')) or (self.type in ('C', 'I')):
                self.update({'type': False})


    @api.onchange('course_id')
    def onchange_course(self):
        context = self._context
        if not context:
            context = {}
        if 'create_inscription' not in context:
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

                diff = 0
                edition_years = []
                if student.edition_id.reference_date:
                    edition_start_year = datetime.strptime(student.edition_id.reference_date, '%Y-%m-%d').year
                    edition_end_year = datetime.now().date().year
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
            last_rec = self.search([('id','>',0),('roll_number','!=', ''),('type','=','C')], order='roll_number desc', limit=1)
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
        elif 'type' in vals and vals['type'] == 'I':
            if 'no_rollno' not in self._context:
                student_roll_no = self.env['ems.student'].browse([vals['student_id']]).roll_number
                vals['roll_number'] = str(student_roll_no) + '.' + str(vals['academic_year'])
            if vals['student_id']:
                student = self.env['ems.student'].browse(vals['student_id'])
                edition_id = student.edition_id.id or False
                course_id = student.course_id.id or False
            else:
               self.update({'edition_id': False, 'course_id': False, 'subject_ids_copy':[[6,0,[]]]})
        #check Roll number for duplicates :
        rollno = vals['roll_number']
        matriculas = self.search([('roll_number','=',rollno)])
        if matriculas and vals['type'] not in ('CC', 'T', 'MC', 'M'):
            raise ValidationError(_('Student Already exists with Roll Number %s')%(rollno))
        return super(EmsEnrollment, self).create(vals)

    @api.multi
    def write(self, vals):
        #check Roll number for duplicates :
        if 'roll_number' in vals or 'type' in vals:
            rollno = self.roll_number
            if 'roll_no' in vals:
                rollno = vals['roll_number']
            ttype = self.type
            if 'type' in vals: 
                ttype = vals['type']
            matriculas = self.search([('roll_number','=',rollno), ('id','!=',self.id)])
            if matriculas and ttype not in ('CC', 'T', 'MC', 'M'):
                raise ValidationError(_('Student Already exists with Roll Number %s')%(rollno))
        return super(EmsEnrollment, self).write(vals)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """ This function filters subjects list on Classes based on Subject & Academic Year selected.
        * returns : list of Inscription Enrollments
        """
        context = self._context or {}
        user = context.get('uid', False)
        if context and 'subject_academic_year_filter' in context and context['subject_academic_year_filter'] is True:
            subject_id = context['subject_id']
            academic_year = context['academic_year']
            university_center_id = context['university_center_id']

            check = False
            message = []
            if not academic_year or not subject_id or not university_center_id:
                check = True
            if not academic_year:
                message.append('Academic Year')
            if not subject_id:
                message.append('Subject')
            if not university_center_id:
                message.append('University Center')
            if check is True:
                msg = ', '.join(message)
                raise UserError(_('Please Select %s.')%(msg))

            query = """ select e.id from ems_enrollment e, ems_subject s, ems_enrollment_inscription_subject i, ems_edition ed, ems_university_center univ
            		where e.id=i.id and
            			  i.subject_id = s.id and
            			  i.subject_id = %s and
                          e.edition_id = ed.id and
                          ed.university_center_id = univ.id and
                          univ.id = %s and
            			  e.academic_year = '%s' """%(subject_id, university_center_id, academic_year)
            self._cr.execute(query)
            result = self._cr.fetchall()
            enrollments = []
            for res in result:
                res = list(res)
                enrollments.append(res[0])
            args += [('id','in', enrollments)]
        return super(EmsEnrollment, self).search(args, offset, limit, order, count=count)

    @api.multi
    def action_load_subjects(self):
        """Load related Course - Semester Subjects in Inscription Enrollments
        """
        for enrollment in self:
            if enrollment.course_year:
                year = int(enrollment.course_year)
                sem1, sem2 = (year*2)-1, year*2
                sem1 = str(sem1)
                sem2 = str(sem2)
                subjects, invalid_subjects = [], []

                #1. get all edition - course plan (semester) subjects:
                edition_sem_subjects = []
                course_plan_id = False
                if enrollment.course_plan_id:
                    course_plan_id = enrollment.course_plan_id.id
                    sem_subject_ids = self.env['ems.course.plan.subject'].search([('course_plan_id','=',enrollment.course_plan_id.id),('semester','in',(str(sem1), str(sem2)))])
                    for sem_subject in sem_subject_ids:
                        edition_sem_subjects.append(sem_subject.subject_id.id)
                elif enrollment.edition_id and enrollment.edition_id.course_plan_id:
                    course_plan_id = enrollment.edition_id.course_plan_id.id
                    sem_subject_ids = self.env['ems.course.plan.subject'].search([('course_plan_id','=',enrollment.edition_id.course_plan_id.id),('semester','in',(str(sem1), str(sem2)))])
                    for sem_subject in sem_subject_ids:
                        edition_sem_subjects.append(sem_subject.subject_id.id)
                #2. get old inscription subjects :
                inscriptions = self.env['ems.enrollment'].search([('type','=','I'),('student_id','=',enrollment.student_id.id)])
                for insc in inscriptions:
                    for subj_line in insc.subject_line:
                        if subj_line.semester in (sem1, sem2) and subj_line.grade >= 10:
                            subjects.append(subj_line.subject_id.id)

                #update semester subjects by removing student's other inscriptions same subjects:
                subjects2 = []
                for sb in edition_sem_subjects:
                   if sb not in subjects:
                       subjects2.append(sb)

                #3. get current inscription subjects if present
                current_subjects = []
                for line in enrollment.subject_line:
                    #if line.subject_id.semester in (sem1, sem2):
                        current_subjects.append(line.subject_id.id)
                #update subjects list by removing already present subjects:
                new_subjects = []
                for sb in subjects2:
                    if sb not in current_subjects:
                        new_subjects.append(sb)
                #4. get subjects from previous semesters with grade < 10:
                semesters = []
                oldsem_subjects = []
                for sm in range(1, int(sem1)):
                    semesters.append(str(sm))
                if semesters:
                    inscriptions = self.env['ems.enrollment'].search([('type','=','I'), ('id','!=',enrollment.id),
                                                                      ('student_id','=',enrollment.student_id.id)])
                    for insc in inscriptions:
                        for subj_line in insc.subject_line:
                            if subj_line.semester in semesters:
                                if subj_line.grade < 10 and subj_line.subject_id.id not in oldsem_subjects:
                                    oldsem_subjects.append(subj_line.subject_id.id)
                                elif subj_line.grade >= 10 and subj_line.subject_id.id in oldsem_subjects:
                                    oldsem_subjects.pop(oldsem_subjects.index(subj_line.subject_id.id))
                    new_subjects.extend(oldsem_subjects)
                    new_subjects = list(set(new_subjects))
                #5. create Grade line for Each Semester Subject:
                if new_subjects:
                    sem_subject_ids = self.env['ems.course.plan.subject'].search([('course_plan_id','=',course_plan_id),('subject_id','in',new_subjects)])
                    for sem_subject in sem_subject_ids:
                        self.env['ems.enrollment.inscription.subject'].create({
                                'inscription_id': enrollment.id,
                                'subject_id': sem_subject.subject_id.id,
                                'semester': sem_subject.semester or sem_subject.subject_id.semester,
                                'semester_copy': sem_subject.semester or sem_subject.subject_id.semester,
                                'course_year': sem_subject.course_year or False,
                        })

                #invalid_subjects = self.env['ems.enrollment.inscription.subject'].search([
                #                        ('inscription_id','=',enrollment.id),   
                #                        ('semester','not in', (str(sem1),str(sem2))) ])
                #for line in invalid_subjects:
                #    line.unlink()            
                        
    @api.one
    def action_validate(self):
        return self.write({'state': 'validate'})
            

class EmsEnrollmentInscriptionSubject(models.Model):
    _name = "ems.enrollment.inscription.subject"
    _description = "Grades"
    _order = "course_year,semester,ordering"

    @api.one
    @api.depends('subject_id')
    def _get_course_plan_ordering(self):
        for ins_line in self:
            subject = ins_line.subject_id.id
            if ins_line.inscription_id.course_plan_id:
                for sub in ins_line.inscription_id.course_plan_id.subject_line:
                    if sub.subject_id.id == subject:
                        self.ordering = sub.ordering

    @api.onchange('subject_id', 'semester', 'ect')
    def onchange_subject(self):
        context = self._context
        vals = {}
        subject_id = self.subject_id.id
        if context and 'edition_id' in context:
            edition_id = context['edition_id']
            course_plan_id = context.get('course_plan_id', False)
            if not course_plan_id:
                course_plan_id = self.env['ems.edition'].browse([edition_id])[0].course_plan_id
                course_plan_id = course_plan_id and course_plan_id.id or False
            ems_edition_subject_id = self.env['ems.course.plan.subject'].search([('subject_id','=',subject_id),('course_plan_id','=',course_plan_id)])
            if ems_edition_subject_id:
                vals['semester'] = ems_edition_subject_id.semester
                vals['ect'] = ems_edition_subject_id.ects
                vals['semester_copy'] = ems_edition_subject_id.semester
                vals['ect_copy'] = ems_edition_subject_id.ects
        else:
            vals['semester'] = self.semester
            vals['ect'] = self.ect
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
    equivalence = fields.Boolean(string="Equivalence", default=False)
    course_year = fields.Char(string='Course Year')
    ordering = fields.Integer(compute="_get_course_plan_ordering", string="Ordering", store=True)
    course_report = fields.Char('Course Report')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
