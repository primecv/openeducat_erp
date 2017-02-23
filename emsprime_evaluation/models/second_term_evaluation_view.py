# -*- coding: utf-8 -*-

from openerp import fields, models
from openerp import tools

class second_term_evaluation_view(models.Model):
    _name = "second.term.evaluation.view"
    _auto = False
    _description = "Second Term Evaluation View"

    id = fields.Integer('Id')
    evaluation_id = fields.Many2one('ems.evaluation', 'Evaluation')
    min_marks = fields.Float('Passing Marks')
    total_marks = fields.Float('Total Marks')
    exam_type = fields.Many2one('ems.evaluation.type', 'Exam Type')
    exam_code = fields.Char('Exam Code', size=8)
    academic_year = fields.Char('Academic Year')
    university_center_id = fields.Many2one('ems.university.center', 'University Center')
    faculty_id = fields.Many2one('ems.faculty', 'Faculty')
    subject_id = fields.Many2one('ems.subject', 'Subject')
    class_id = fields.Many2one('ems.class', 'Class')
    continuous_evaluation = fields.Boolean('Continuous Evaluation', default=False)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'second_term_evaluation_view')
        cr.execute("""
            CREATE OR REPLACE VIEW second_term_evaluation_view AS (
select (row_number() OVER(ORDER BY v.evaluation_id)) AS id,v.*
from (select id as evaluation_id,min_marks,total_marks,exam_type,exam_code,academic_year,university_center_id,faculty_id,subject_id,class_id,continuous_evaluation 
from ems_evaluation where continuous_evaluation is true and state='done' and id in (select evaluation_id from ems_evaluation_student where status='Reprovado')
union
select id as evaluation_id,min_marks,total_marks,exam_type,exam_code,academic_year,university_center_id,faculty_id,subject_id,class_id,continuous_evaluation 
from ems_evaluation where continuous_evaluation is false and state='done' and id in (select evaluation_id from ems_evaluation_attendee where final_grade<10 and exam_type=3)) v)""")

