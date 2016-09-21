#-*- coding: utf-8

from openerp import models, fields, api
import random

def random_token():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(10))

class wizard_student_user_link(models.TransientModel):
	_name = "wizard.student.user"
	_description = "Create User related to Students by Course"

	course_id = fields.Many2one('ems.course', 'Course')
	result = fields.Html('Result')

	@api.multi
	def action_generate(self):
		for wiz in self:
			course_id = wiz.course_id.id
			students = self.env['ems.student'].search([('course_id', '=', course_id)])
			matricula_students = []
			for student in students:
				if not student.user_id:
					for enrollment in student.roll_number_line:
						if enrollment.type == 'M':
							matricula_students.append(student)
							break
			student_group = self.env.ref('emsprime_core.group_ems_student')
			student_group = student_group and student_group.id or False
			for student in matricula_students:
				name = ' '.join(filter(bool, [student.name, student.middle_name, student.last_name]))
				if student.institutional_email:
					user_id = self.env['res.users'].create({
							'name': name,
							'password': random_token(),
							'university_center_id': student.university_center_id and student.university_center_id.id or False,
							'email': student.institutional_email,
							'login': student.institutional_email,
							'groups_id': [[6, 0, [student_group]]]
						})
					student.write({'user_id': user_id.id})
					user_id.action_reset_password()


