# -*- coding: utf-8 -*-

from openerp import fields, models
from openerp import tools

class enrollment_grades_report(models.Model):
    _name = "enrollment.grades.report"
    _auto = False
    _description = "Enrollment Grades"

    id = fields.Integer('Id')
    student_id = fields.Many2one('ems.student', 'Student')
    course_id = fields.Many2one('ems.course', 'Course')
    edition_id = fields.Many2one('ems.edition', 'Edition')
    subject_id = fields.Many2one('ems.subject', 'Subject')
    semester = fields.Char('Semester')
    grade = fields.Integer('Grade', group_operator="avg")
    university_center_id = fields.Many2one('ems.university.center', 'University Center')

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'enrollment_grades_report')
        cr.execute("""
            CREATE OR REPLACE VIEW enrollment_grades_report AS (
				select e.student_id as student_id, 
						e.course_id as course_id, 
						e.edition_id as edition_id, 
						el.subject_id as subject_id, 
						el.semester as semester,
						el.grade as grade,
						s.university_center_id as university_center_id,
						el.id as id
					from ems_student s, ems_enrollment e, ems_enrollment_inscription_subject el 
				where s.id=e.student_id and 
					  e.id=el.inscription_id)""")

