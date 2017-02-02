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
            res.update(continuous_evaluation = True)
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
            res.update(continuous_evaluation = True)
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
            #print "ENTROU EXAME::::::::::::::::::::::::::"
            for evaluation in self:
                existing_students = []
                for line in evaluation.attendees_line:
                    #print "FOR 1::::::::::::"
                    #print line.student_id.id
                    existing_students.append(line.student_id.id)
                class_students = []
                for enrollment in evaluation.class_id.enrollment_line:
                    #print "FOR 2::::::::::::"
                    #print enrollment.student_id.id
                    if enrollment.evaluation_type=='regular_exam':
                        #print "IF 1::::::::::::"
                        #print enrollment.evaluation_type
                        class_students.append(enrollment.student_id.id)
                for student in class_students:
                    if student in existing_students:
                        class_students.remove(student)
                for student in class_students:
                    line_ids.append([0, False,{'student_id': student, 'status': 'present'}])
            self.attendees_line = line_ids
        else:
            #print "ENTROU CONTINUOUS::::::::::::::::::::::::::"
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
		
    @api.model
    def create(self, vals):
        res = super(OpEvaluation, self).create(vals)
        ln_ids = []
        elems_percentage=0
        if not res.element_line and self.continuous_evaluation is True:
            raise ValidationError("Please add the evaluation elements.")

        if self.continuous_evaluation is True:
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
            grade_int = int(grade)
        return grade_int

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
            print "GRADE INT::::::::::::::::::::::::::::::::::::::"
            print grade_int
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
                grade_str = "14 (Quatorze)"
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
		
    evaluation_id = fields.Many2one('ems.evaluation', string='Evaluation')
    student_id = fields.Many2one('ems.student', string='Student')
    grade = fields.Float('Grade')
    element_line = fields.One2many(
        'ems.evaluation.student.element', 'evaluation_student_id', 'Elements')
    grade_string = fields.Char(string='Grade (String)', compute='_get_grade_str', store=True)

    @api.multi
    def write(self, vals):
        res = super(EmsEvaluationStudents, self).write(vals)
        percentage=0.0
        grade=0.0
        total_grade=0.0
        grade2=0.0
        all_grades_delivered=False
        for ln in self.element_line:
            element_id=ln.element_id.id
            grade=ln.grade
            #element = self.env['ems.evaluation.element'].browse(element_id)
            elements = self.env['ems.evaluation.element'].search([('element_id','=',element_id),('evaluation_id','=',self.evaluation_id.id)])
            if elements:
                for element in elements:
                    percentage=element.percentage / float(100)
                    grade2=percentage * grade
            if grade2==0:
                all_grades_delivered=True
            total_grade=total_grade + grade2
        if all_grades_delivered is True:
            total_grade=0
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

    _sql_constraints = [('uniq_evaluation_element','unique(evaluation_id, element_id)','Element must be Unique per Evaluation.')]

class EmsEvaluationStudentElements(models.Model):
    _name = "ems.evaluation.student.element"
    _description = "Evaluation Student Elements"
    _rec_name = "element_id"

    evaluation_student_id = fields.Many2one('ems.evaluation.student', string='Student Evaluation')
    element_id = fields.Many2one('ems.element', string='Element')
    grade = fields.Float('Grade')
    status = fields.Selection(
        [('F', 'Missed'), ('D', 'Gave up'), ('A', 'Nullified')], 'Eval. Status', select=True, track_visibility='onchange')
		
    _sql_constraints = [('uniq_evaluation_student_element','unique(evaluation_student_id, element_id)','Element must be Unique per Student Evaluation.')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
