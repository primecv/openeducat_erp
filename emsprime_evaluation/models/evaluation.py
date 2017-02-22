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
from openerp import models, fields, api
from openerp.exceptions import ValidationError
import base64, re
from lxml import etree
from openerp.osv.orm import setup_modifiers


class OpEvaluation(models.Model):
    _name = 'ems.evaluation'
    _rec_name = 'class_id'
    _inherit = 'mail.thread'
    _description = 'Exam'

    @api.one
    @api.depends('element_line')
    def _get_formula(self):
        element_formula = []
        element_formula_name = ''
        element_percentage=0
        for line in self.element_line:
            element_name=line.element_id.name
            element_percentage=line.percentage
            element_formula_name=element_name + ' * ' + str(element_percentage) + '%'
            element_formula.append(element_formula_name) 
        result = ' + '.join(element_formula)
        self.elements_formula = result

    #session_id = fields.Many2one('ems.evaluation.session', 'Exam Session')
    faculty_id = fields.Many2one('ems.faculty', string='Faculty', required=True)
    subject_id = fields.Many2one('ems.subject', 'Subject', required=True)
    class_id = fields.Many2one('ems.class', 'Class', required=True)
    exam_code = fields.Char('Exam Code', size=8)
    exam_type = fields.Many2one('ems.evaluation.type', 'Exam Type')
    #evaluation_type = fields.Selection(
    #    [('normal', 'Normal'), ('GPA', 'GPA'), ('CWA', 'CWA'), ('CCE', 'CCE')],
    #    'Evaluation Type', default="normal", required=True)
    attendees_line = fields.One2many(
        'ems.evaluation.attendee', 'evaluation_id', 'Attendees')
    #venue = fields.Many2one('res.partner', 'Venue')
    start_time = fields.Datetime('Start Time')
    end_time = fields.Datetime('End Time')
    state = fields.Selection(
        [('new', 'New Exam'), ('schedule', 'Scheduled'), ('held', 'Held'),
         ('cancel', 'Cancelled'), ('done', 'Done')], 'State', select=True,
        readonly=True, default='new', track_visibility='onchange')
    note = fields.Text('Note')
    responsible_id = fields.Many2many('ems.faculty', string='Responsible')
    #name = fields.Char('Exam', size=256, required=True)
    total_marks = fields.Float('Total Marks')
    min_marks = fields.Float('Passing Marks')
    room_id = fields.Many2one('ems.evaluation.room', 'Room')
    academic_year = fields.Selection([('2016', '2016/2017'),('2015', '2015/2016'), ('2014', '2014/2015'),('2013', '2013/2014'),('2012', '2012/2013'), 
                                      ('2011', '2011/2012'), ('2010', '2010/2011'), ('2009', '2009/2010'), ('2008', '2008/2009'), ('2007', '2007/2008'),
									  ('2006', '2006/2007'), ('2005', '2005/2006'), ('2004', '2004/2005'), ('2003', '2003/2004'),('2002', '2002/2003'),
									  ('2001', '2001/2002'),('2000', '2000/2001'),('1999', '1999/2000'),('1998', '1998/1999'),('1997', '1997/1998'),
									  ('1996', '1996/1997'), ('1995', '1995/1996'),('1994', '1994/1995'),('1993', '1993/1994'),('1992', '1992/1993'),
									  ('1991', '1991/1992')
            ], 'Academic Year', track_visibility='onchange', required=True)
    university_center_id = fields.Many2one('ems.university.center', 'University Center', required=True)
    continuous_evaluation = fields.Boolean('Continuous Evaluation', default=False)
    student_line = fields.One2many(
        'ems.evaluation.student', 'evaluation_id', 'Students')
    element_line = fields.One2many(
        'ems.evaluation.element', 'evaluation_id', 'Elements')
    #state_continuous = fields.Selection([('draft', 'Draft'), ('validate', 'Validated'),('done', 'Done')],'State Continuous', default="draft", track_visibility='onchange', select=True)
    elements_formula = fields.Char(compute="_get_formula", string="Elements Formula", store=True)
    use_code = fields.Boolean('Use code in report', default=False)

    @api.model
    def default_get(self, fields=None):
        res = super(OpEvaluation, self).default_get(fields)
        context = self._context
        if context and 'get_faculty_user_id' in context:
            user_id = self._uid
            faculty = self.env['ems.faculty'].search([('user_id', '=', user_id)])
            if faculty:
                res.update(faculty_id = faculty.id)
                if faculty.university_center_id:
                    res.update(university_center_id = faculty.university_center_id.id)
        if context and 'get_continuous_evaluation' in context:
            #print "DEFAULT GET - CONTINUOUS"
            #print context['get_continuous_evaluation']
            res.update(continuous_evaluation = True)
        if context and 'get_regular_evaluation' in context:
            #print "DEFAULT GET - REGULAR"
            #print context['get_regular_evaluation']
            res.update(continuous_evaluation = False)
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """ Make Faculty & University Center fields non-editable
        if Evaluation is created by Faculty User.
        """
        res = super(OpEvaluation, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        context = self._context
        if view_type == 'form' and context and 'get_faculty_user_id' in context:
            user_id = self._uid
            faculty = self.env['ems.faculty'].search([('user_id', '=', user_id)])
            if faculty:
                for node in doc.xpath("//field[@name='faculty_id']"):
                    node.set('readonly', '1')
                    setup_modifiers(node, res['fields']['faculty_id'])
                    res['arch'] = etree.tostring(doc)
                if faculty.university_center_id:
                    for node in doc.xpath("//field[@name='university_center_id']"):
                        node.set('readonly', '1')
                        setup_modifiers(node, res['fields']['university_center_id'])
                        res['arch'] = etree.tostring(doc)
        if context and 'get_continuous_evaluation' in context:
            #print "FIELDS VIEW GET - CONTINUOUS"
            #print context['get_continuous_evaluation']
            res.update(continuous_evaluation = True)
        if context and 'get_regular_evaluation' in context:
            #print "FIELDS VIEW GET - REGULAR"
            #print context['get_regular_evaluation']
            res.update(continuous_evaluation = False)
        return res

    @api.constrains('total_marks', 'min_marks')
    def _check_marks(self):
        if self.total_marks <= 0.0 or self.min_marks <= 0.0:
            raise ValidationError('Enter proper marks!')
        if self.min_marks > self.total_marks:
            raise ValidationError(
                "Passing Marks can't be greater than Total Marks")

    @api.constrains('start_time', 'end_time')
    def _check_date_time(self):
        if self.start_time > self.end_time:
            raise ValidationError('End Time cannot be set before Start Time.')

    @api.onchange('university_center_id')
    def onchange_university_center_id(self):
        context = self._context
        if not context or 'get_faculty_user_id' not in context:
            self.faculty_id = False

    @api.onchange('faculty_id')
    def onchange_faculty_id(self):
        self.subject_id = False

    @api.onchange('subject_id')
    def onchange_subject_id(self):
        self.class_id = False

    @api.onchange('class_id')
    def onchange_class_id(self):
        """ This function adds Students related to enrollment on selected Class 
        """
        line_ids = []
        result = {}
        if self.continuous_evaluation is False:
            print "ENTROU EXAME::::::::::::::::::::::::::"

            if self.exam_type.special is False:
                for evaluation in self:
                    existing_students = []
                    for line in evaluation.attendees_line:
                        print "FOR 1::::::::::::"
                        print line.student_id.id
                        existing_students.append(line.student_id.id)
                    class_students = []
                    for enrollment in evaluation.class_id.enrollment_line:
                        print "FOR 2::::::::::::"
                        print enrollment.student_id.id
                        if enrollment.evaluation_type=='regular_exam':
                            print "IF 1::::::::::::"
                            print enrollment.evaluation_type
                            class_students.append(enrollment.student_id.id)
                    for student in class_students:
                        if student in existing_students:
                            class_students.remove(student)
                    for student in class_students:
                        line_ids.append([0, False,{'student_id': student}])
                self.attendees_line = line_ids
            else:
                for evaluation in self:
                    existing_students = []
                    for line in evaluation.attendees_line:
                        print "FOR 3::::::::::::"
                        print line.student_id.id
                        existing_students.append(line.student_id.id)
                    evaluation_students = []
                    '''for enrollment in evaluation.class_id.enrollment_line:
                        print "FOR 4::::::::::::"
                        print enrollment.student_id.id
                        #if enrollment.evaluation_type=='regular_exam':
                        #    print "IF 1::::::::::::"
                        #    print enrollment.evaluation_type
                        class_students.append(enrollment.student_id.id)
                    for student in class_students:
                        if student in existing_students:
                            class_students.remove(student)'''
                    student_continuous_ids = self.env['ems.evaluation.student'].search([('class_id','=',self.class_id.id),('status','=','Reprovado')])
                    failed_students_continuous = []
                    for st1 in student_continuous_ids:
                        print "Failed Continuous::::::::::::::::::::::::::::::"
                        print st1.student_id.id
                        failed_students_continuous.append(st1.student_id.id)
                    for st2 in failed_students_continuous:
                        if st2 in existing_students:
                            failed_students_continuous.remove(st2)
                    for st3 in failed_students_continuous:
                        evaluation_students.append(st3)

                    student_exam_ids = self.env['ems.evaluation.attendee'].search([('class_id','=',self.class_id.id),('final_grade','<',10)])
                    failed_students_exam = []
                    for st4 in student_exam_ids:
                        print "Failed Exam::::::::::::::::::::::::::::::"
                        print st1.student_id.id
                        failed_students_exam.append(st4.student_id.id)
                    for st5 in failed_students_exam:
                        if st5 in existing_students:
                            failed_students_exam.remove(st5)
                    for st6 in failed_students_exam:
                        evaluation_students.append(st6)

                    for student in evaluation_students:
                        line_ids.append([0, False,{'student_id': student}])
                self.attendees_line = line_ids


        else:
            print "ENTROU CONTINUOUS::::::::::::::::::::::::::"
            for evaluation in self:
                existing_students = []
                for line in evaluation.student_line:
                    #print "FOR 1::::::::::::"
                    #print line.student_id.id
                    existing_students.append(line.student_id.id)
                class_students = []
                for enrollment in evaluation.class_id.enrollment_line:
                    #print "FOR 2::::::::::::"
                    #print enrollment.student_id.id
                    if enrollment.evaluation_type=='continuous':
                        #print "IF 1::::::::::::"
                        #print enrollment.evaluation_type
                        class_students.append(enrollment.student_id.id)
                for student in class_students:
                    if student in existing_students:
                        class_students.remove(student)
                for student in class_students:
                    line_ids.append([0, False,{'student_id': student}])
            self.student_line = line_ids

    '''def onchange_class_id(self):
        """ This function adds Students related to enrollment on selected Class 
        """
        line_ids = []
        result = {}
        if self.continuous_evaluation is False:
            for evaluation in self:
                existing_students = []
                for line in evaluation.attendees_line:
                    existing_students.append(line.student_id.id)
                class_students = []
                for enrollment in evaluation.class_id.enrollment_ids:
                    class_students.append(enrollment.student_id.id)
                for student in class_students:
                    if student in existing_students:
                        class_students.remove(student)
                for student in class_students:
                    line_ids.append([0, False,{'student_id': student, 'status': 'present'}])
            self.attendees_line = line_ids
        else:
            for evaluation in self:
                existing_students = []
                for line in evaluation.student_line:
                    existing_students.append(line.student_id.id)
                class_students = []
                for enrollment in evaluation.class_id.enrollment_ids:
                    class_students.append(enrollment.student_id.id)
                for student in class_students:
                    if student in existing_students:
                        class_students.remove(student)
                for student in class_students:
                    line_ids.append([0, False,{'student_id': student}])
            self.student_line = line_ids'''

    @api.one
    def act_held(self):
        self.state = 'held'

    @api.one
    def act_done(self):
        self.state = 'done'

    @api.one
    def act_schedule(self):
        self.state = 'schedule'

    @api.one
    def act_cancel(self):
        self.state = 'cancel'

    @api.one
    def act_new_exam(self):
        self.state = 'new'


    @api.multi
    def action_print(self):
        report_name="emsprime_evaluation.report_continuous_evaluation"
        report = self.env['report'].get_pdf(self, report_name)
        result = base64.b64encode(report)
        file_name = str(report_name.encode('utf-8')) + '.pdf'

        return self.env['report'].get_action(self, report_name)

    @api.multi
    def action_print_exam(self):
        report_name="emsprime_evaluation.report_evaluation"
        report = self.env['report'].get_pdf(self, report_name)
        result = base64.b64encode(report)
        file_name = str(report_name.encode('utf-8')) + '.pdf'

        return self.env['report'].get_action(self, report_name)

    @api.model
    def create(self, vals):
        res = super(OpEvaluation, self).create(vals)
        ln_ids = []
        elems_percentage=0
        if not res.element_line and res.continuous_evaluation is True:
            raise ValidationError("Please add the evaluation elements.")

        if res.continuous_evaluation is True:
            for ln in res.element_line:
                ln_ids.append(ln.element_id.id)
                elems_percentage = elems_percentage + ln.percentage

            if elems_percentage > 100:
                raise ValidationError("The percentage of the elements cannot be greater than 100.")

            for line in res.student_line:
                evaluation_student_id=line.id
                #cont=0
                #for line2 in res.element_line:
                for r in range(0, len(ln_ids)):
                    vals = {
                        'evaluation_student_id': evaluation_student_id,
                        'element_id': ln_ids[r]
                        #'element_id': line2.element_id.id
                    }
                    #cont = cont + 1
                    eval_student_element = self.env['ems.evaluation.student.element'].create(vals)
        
        return res

    @api.multi
    def write(self, vals):
        res = super(OpEvaluation, self).write(vals)
        ln_ids = []
        student_elem_ids = []
        elems_percentage=0
        if not self.element_line and self.continuous_evaluation is True:
            raise ValidationError("Please add the evaluation elements.")

        if self.continuous_evaluation is True:
            for ln in self.element_line:
                ln_ids.append(ln.element_id.id)
                elems_percentage = elems_percentage + ln.percentage

            if elems_percentage > 100:
                raise ValidationError("The percentage of the elements cannot be greater than 100.")

            for line in self.student_line:
                evaluation_student_id=line.id
                for elem_line in line.element_line:
                    student_elem_ids.append(elem_line.element_id.id)
                for student in student_elem_ids:
                    if student not in ln_ids:
                        self._cr.execute("""DELETE FROM ems_evaluation_student_element WHERE evaluation_student_id =%s AND element_id=%s"""%(evaluation_student_id,student))
                for elem in ln_ids:
                    if elem not in student_elem_ids:
                        self._cr.execute("""INSERT INTO ems_evaluation_student_element (evaluation_student_id,element_id) VALUES (%s,%s)"""%(evaluation_student_id,elem))

                self._cr.execute("""select count(*) as count from ems_evaluation_student_element WHERE evaluation_student_id=%s"""%(evaluation_student_id))
                result = self._cr.fetchone()
                if result:
                    result = result[0]
                    if result == 0:
                        for elem in ln_ids:
                            self._cr.execute("""INSERT INTO ems_evaluation_student_element (evaluation_student_id,element_id) VALUES (%s,%s)"""%(evaluation_student_id,elem))


        return res

    @api.multi
    def get_elements_names(self, element_line=False):
        result = []
        if element_line:
            for element in element_line:
                lines = {}
                lines['element'] = element.element_id.name
                result.append(lines)
        return result

    @api.multi
    def get_grade_int(self, grade=False):
        grade_int = 0
        if grade:
            if (grade).is_integer():
                grade_int = int(grade)
            else: 
                grade_int = grade
        return grade_int

    @api.multi
    def action_load_foreign_ids(self):
        """Load ids
        """
        student_ids = self.env['ems.evaluation.student.element'].search([('id','>',0)])

        for student in student_ids:
            evaluation_student_id=student.id
            faculty_id=student.evaluation_student_id.evaluation_id.faculty_id.id
            subject_id=student.evaluation_student_id.evaluation_id.subject_id.id
            student_id=student.evaluation_student_id.student_id.id
            class_id=student.evaluation_student_id.evaluation_id.class_id.id
            academic_year=student.evaluation_student_id.evaluation_id.academic_year
            roll_number=student.evaluation_student_id.student_id.roll_number
            student_name=student.evaluation_student_id.student_id.complete_name
            faculty_name=student.evaluation_student_id.evaluation_id.faculty_id.complete_name
            
            eval_id = self.env['ems.evaluation.student.element'].browse(evaluation_student_id)
            eval_id.write({'faculty_id': faculty_id,'subject_id':subject_id,'student_id':student_id,'class_id':class_id,'academic_year':academic_year,'roll_number':roll_number,'student_name':student_name,'faculty_name':faculty_name})
	
    @api.multi
    def action_load_exams_foreign_ids(self):
        """Load ids
        """
        student_ids = self.env['ems.evaluation.attendee'].search([('id','>',0)])

        for student in student_ids:
            attendee_id=student.id
            faculty_id=student.evaluation_id.faculty_id.id
            subject_id=student.evaluation_id.subject_id.id
            student_id=student.student_id.id
            academic_year=student.evaluation_id.academic_year
            class_id=student.evaluation_id.class_id.id
            roll_number=student.student_id.roll_number
            student_name=student.student_id.complete_name
            faculty_name=student.evaluation_id.faculty_id.complete_name
            
            eval_id = self.env['ems.evaluation.attendee'].browse(attendee_id)
            eval_id.write({'faculty_id': faculty_id,'subject_id':subject_id,'student_id':student_id,'class_id':class_id,'academic_year':academic_year,'roll_number':roll_number,'student_name':student_name,'faculty_name':faculty_name})

class EmsEvaluationStudents(models.Model):
    _name = "ems.evaluation.student"
    _description = "Evaluation Students"
    _rec_name = "student_id"
    _order = "student_id"

    @api.one
    @api.depends('grade')
    def _get_grade_str(self):
        grade_str=''
        if self.grade:
            grade_int=int(self.grade)
            if grade_int==1:
                grade_str = "1 (Um)"
            elif grade_int ==2:
                grade_str = "2 (Dois)"
            elif grade_int ==3:
                grade_str = "3 (Três)"
            elif grade_int ==4:
                grade_str = "4 (Quatro)"
            elif grade_int ==5:
                grade_str = "5 (Cinco)"
            elif grade_int ==6:
                grade_str = "6 (Seis)"
            elif grade_int ==7:
                grade_str = "7 (Sete)"
            elif grade_int ==8:
                grade_str = "8 (Oito)"
            elif grade_int ==9:
                grade_str = "9 (Nove)"
            elif grade_int ==10:
                grade_str = "10 (Dez)"
            elif grade_int ==11:
                grade_str = "11 (Onze)"
            elif grade_int ==12:
                grade_str = "12 (Doze)"
            elif grade_int ==13:
                grade_str = "13 (Treze)"
            elif grade_int ==14:
                grade_str = "14 (Catorze)"
            elif grade_int ==15:
                grade_str = "15 (Quinze)"
            elif grade_int ==16:
                grade_str = "16 (Dezasseis)"
            elif grade_int ==17:
                grade_str = "17 (Dezassete)"
            elif grade_int ==18:
                grade_str = "18 (Dezoito)"
            elif grade_int ==19:
                grade_str = "19 (Dezanove)"
            elif grade_int ==20:
                grade_str = "20 (Vinte)"
        else:
            grade_str = "a)"
        self.grade_string = grade_str

    @api.one
    @api.depends('grade')
    def _get_status(self):
        elements = self.env['ems.evaluation.element'].search([('evaluation_id','=',self.evaluation_id.id),('is_test','=',True)])
        #print "EVALUATION ID:::::::::::::::::"
        #print self.evaluation_id.id
  
        grade_student=self.grade
        count_elements=0
        grade=0.0
        elements_list = []
        final_grade=0.0
        failed_test=False
        for element in elements:
            elements_list.append(element.element_id.id)
            #print "ELEMENT:::::::::::::::::"
            #print element.element_id.id
            count_elements=count_elements + 1
        student_elements = self.env['ems.evaluation.student.element'].search([('element_id','in',elements_list),('evaluation_student_id','=',self.id)])
        for st in student_elements:
            grade=grade+st.grade
            if st.status:
                #print "ENTROU STATUS:::::::::::::::::::::::::::::::::::"
                failed_test=True
            #print "Student grades"
            #print st.grade
        if count_elements > 0:
            final_grade = grade / count_elements
            if final_grade >= 8 and grade_student >=10:
                self.status="Aprovado"
                self.status2="Aprovado"
                self.status3="Aprovado"
            else:
                self.status="Reprovado"
                self.status2="Reprovado"
                self.status3="Reprovado"
        else:
            if grade_student >=10:
                self.status="Aprovado"
                self.status2="Aprovado"
                self.status3="Aprovado"
            else:
                self.status="Reprovado"
                self.status2="Reprovado"
                self.status3="Reprovado"

        if failed_test is True:
            #print "ACTUALIZOU GRADE:::::::::::::::::::::::::::::::::::"
            self.grade_string='a)'
        '''print "COUNT ELEMENTS:::::::::::::::::"
        print count_elements
        print "GRADE:::::::::::::::::"
        print grade
        print "FINAL GRADE:::::::::::::::::"
        print final_grade'''
        

    evaluation_id = fields.Many2one('ems.evaluation', string='Evaluation')
    student_id = fields.Many2one('ems.student', string='Student')
    grade = fields.Float('Grade')
    element_line = fields.One2many(
        'ems.evaluation.student.element', 'evaluation_student_id', 'Elements')
    grade_string = fields.Char(string='Grade (String)', compute='_get_grade_str', store=True)
    status = fields.Char(string='Status', compute='_get_status', store=True)
    status2 = fields.Char(string='Status 2', compute='_get_status', store=True)
    status3 = fields.Char(string='Status 3', compute='_get_status', store=True)
    #JCF - 22-02-2017
    class_id = fields.Many2one('ems.class', related="evaluation_id.class_id", string='Class', store=True, readonly=True)

    @api.multi
    def write(self, vals):
        res = super(EmsEvaluationStudents, self).write(vals)
        percentage=0.0
        grade=0.0
        total_grade=0.0
        grade2=0.0
        all_grades_delivered=False
        failed_test=False
        for ln in self.element_line:
            element_id=ln.element_id.id
            grade=ln.grade
            if ln.element_id.is_test is True and ln.status:
                #print "ENTROU STATUS:::::::::::::::::::::::::::::::::::"
                failed_test=True
            elements = self.env['ems.evaluation.element'].search([('element_id','=',element_id),('evaluation_id','=',self.evaluation_id.id)])
            if elements:
                for element in elements:
                    percentage=element.percentage / float(100)
                    grade2=percentage * (grade + 0.01)
            if grade2==0:
                all_grades_delivered=True
            total_grade=total_grade + grade2
        total_grade=total_grade+0.01
        if all_grades_delivered is True:
            total_grade=0
        if failed_test is True:
            vals['grade']=0.0
        else:
            vals['grade'] = round(total_grade)
        return super(EmsEvaluationStudents, self).write(vals)
		
class EmsEvaluationElements(models.Model):
    _name = "ems.evaluation.element"
    _description = "Evaluation Elements"
    _rec_name = "element_id"
    _order = "element_id"

    evaluation_id = fields.Many2one('ems.evaluation', string='Evaluation')
    element_id = fields.Many2one('ems.element', string='Element')
    percentage = fields.Integer('Percentage')
    is_test = fields.Boolean('Is test?',related='element_id.is_test', track_visibility='onchange', store=True)

    _sql_constraints = [('uniq_evaluation_element','unique(evaluation_id, element_id)','Element must be Unique per Evaluation.')]

class EmsEvaluationStudentElements(models.Model):
    _name = "ems.evaluation.student.element"
    _description = "Evaluation Student Elements"
    _rec_name = "element_id"
    _order = "element_id"
    #_order = "class_id,academic_year,faculty_name,roll_number,student_name"

    @api.one
    @api.depends('evaluation_student_id')
    def _get_data(self):
        faculty_id = False
        subject_id = False
        student_id = False
        class_id = False
        academic_year=''
        student_name=''
        faculty_name=''
        roll_number=''
        if self.evaluation_student_id:
            faculty_id=self.evaluation_student_id.evaluation_id.faculty_id.id
            subject_id=self.evaluation_student_id.evaluation_id.subject_id.id
            student_id=self.evaluation_student_id.student_id.id
            class_id=self.evaluation_student_id.evaluation_id.class_id.id
            academic_year=self.evaluation_student_id.evaluation_id.academic_year
            roll_number=self.evaluation_student_id.student_id.roll_number
            student_name=self.evaluation_student_id.student_id.complete_name
            faculty_name=self.evaluation_student_id.evaluation_id.faculty_id.complete_name
        self.faculty_id=faculty_id
        self.subject_id=subject_id
        self.student_id=student_id
        self.class_id=class_id
        self.academic_year=academic_year
        self.roll_number=roll_number
        self.student_name=student_name
        self.faculty_name=faculty_name
		
    @api.multi
    def write(self, vals):
        res = super(EmsEvaluationStudentElements, self).write(vals)
        percentage=0.0
        grade=0.0
        total_grade=0.0
        grade2=0.0
        all_grades_delivered=False
        for ln in self.evaluation_student_id.element_line:
            element_id=ln.element_id.id
            grade=ln.grade
            elements = self.env['ems.evaluation.element'].search([('element_id','=',element_id),('evaluation_id','=',self.evaluation_student_id.evaluation_id.id)])
            if elements:
                for element in elements:
                    percentage=element.percentage / float(100)
                    grade2=percentage * (grade + 0.01)
            if grade2==0:
                all_grades_delivered=True
            total_grade=total_grade + grade2
        if all_grades_delivered is True:
            total_grade=0
        total_grade = round(total_grade)
        eval_id = self.env['ems.evaluation.student'].browse(self.evaluation_student_id.id)
        eval_id.write({'grade': total_grade})
        return res

    evaluation_student_id = fields.Many2one('ems.evaluation.student', string='Student Evaluation')
    element_id = fields.Many2one('ems.element', string='Element')
    grade = fields.Float('Grade')
    status = fields.Selection(
        [('F', 'Missed'), ('D', 'Gave up'), ('A', 'Nullified')], 'Eval. Status', select=True, track_visibility='onchange')
    faculty_id = fields.Many2one('ems.faculty', string='Faculty', compute='_get_data', store=True, track_visibility='onchange')
    subject_id = fields.Many2one('ems.subject', string='Subject', compute='_get_data', store=True, track_visibility='onchange')
    student_id = fields.Many2one('ems.student', string='Student', compute='_get_data', store=True, track_visibility='onchange')
    class_id = fields.Many2one('ems.class', string='Class', compute='_get_data', store=True, track_visibility='onchange')
    academic_year = fields.Char('Academic Year', compute='_get_data', store=True, track_visibility='onchange')
    roll_number = fields.Char('Roll name', compute='_get_data', store=True, track_visibility='onchange')
    student_name = fields.Char('Student name', compute='_get_data', store=True, track_visibility='onchange')
    faculty_name = fields.Char('Faculty name', compute='_get_data', store=True, track_visibility='onchange')

    _sql_constraints = [('uniq_evaluation_student_element','unique(evaluation_student_id, element_id)','Element must be Unique per Student Evaluation.')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
