# -*- coding: utf-8 -*-

from openerp import fields, models
from openerp import tools

class student_grades_view(models.Model):
    _name = "student.grades.view"
    _auto = False
    _description = "Student Grades View"

    id = fields.Integer('Id')
    student_id = fields.Many2one('ems.student', 'Student')
    evaluation_id = fields.Many2one('ems.evaluation', 'Evaluation')
    university_center_id = fields.Many2one('ems.university.center', 'University Center')
    subject_id = fields.Many2one('ems.subject', 'Subject')
    faculty_id = fields.Many2one('ems.faculty', 'Faculty')
    class_id = fields.Many2one('ems.class', 'Class')
    grade = fields.Integer('Grade')
    academic_year = fields.Char('Academic Year')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'student_grades_view')
        cr.execute("""
            CREATE OR REPLACE VIEW student_grades_view AS (
				select (row_number() OVER(ORDER BY v.student_id)) AS id,v.*
from (select s.student_id, s.evaluation_id, s.grade::integer,e.academic_year,e.university_center_id,e.faculty_id,e.subject_id,e.class_id
from ems_evaluation_student s, ems_evaluation e
where e.id=s.evaluation_id
union
select s.student_id, s.evaluation_id, s.final_grade as grade,e.academic_year,e.university_center_id,e.faculty_id,e.subject_id,e.class_id
from ems_evaluation_attendee s, ems_evaluation e
where e.id=s.evaluation_id) v)""")

