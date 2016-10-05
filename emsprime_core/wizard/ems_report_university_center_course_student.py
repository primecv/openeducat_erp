#-*- coding: utf-8 -*-

from openerp import models, fields, api

class ems_report_university_center_course_student(models.TransientModel):
	_name = "ems.report.university.center.course.student"
	_description = "Students by Unviersity Center & Course"

	university_center_id = fields.Many2one('ems.university.center', 'University Center')
	course_id = fields.Many2one('ems.course', 'Course')
	academic_year = fields.Selection([('2016', '2016/2017'),('2015', '2015/2016'), ('2014', '2014/2015'),('2013', '2013/2014'),('2012', '2012/2013'), 
                                      ('2011', '2011/2012'), ('2010', '2010/2011'), ('2009', '2009/2010'), ('2008', '2008/2009'), ('2007', '2007/2008'),
									  ('2006', '2006/2007'), ('2005', '2005/2006'), ('2004', '2004/2005'), ('2003', '2003/2004'),('2002', '2002/2003'),
									  ('2001', '2001/2002'),('2000', '2000/2001'),('1999', '1999/2000'),('1998', '1998/1999'),('1997', '1997/1998'),
									  ('1996', '1996/1997'), ('1995', '1995/1996'),('1994', '1994/1995'),('1993', '1993/1994'),('1992', '1992/1993'),
									  ('1991', '1991/1992')
            ], 'Academic Year', track_visibility='onchange')
	course_year = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], 'Course Year',track_visibility='onchange')
	subject_id = fields.Many2one('ems.subject', 'Subject')

	@api.onchange('course_id')
	def onchange_course(self):
		self.subject_id = False

	@api.multi
	def get_student_list(self, university_center_id, course_id, academic_year=False, course_year=False, subject_id=False):
		query = """select s.id,s.roll_number from ems_student s, ems_enrollment e, ems_enrollment_inscription_subject ie 
						where s.id=e.student_id and ie.inscription_id = e.id and
						e.type='I' and 
						s.university_center_id=%s and 
						e.course_id=%s
					"""%(university_center_id, course_id)
		if academic_year:
			query = query + "and e.academic_year='%s'"%(academic_year)
		if course_year:
			query = query + "and e.course_year='%s'"%(course_year)
		if subject_id:
			query = query + "and ie.subject_id='%s'"%(subject_id)
		query = query + 'order by s.roll_number'
		self._cr.execute(query)
		result = self._cr.fetchall()
		students = []
		for res in result:
			res = list(res)
			students.append(res[0])
		result = []
		if students:
			result = self.env['ems.student'].search([('id','in',students)], order="complete_name")
		return result


	@api.multi
	def print_report(self):
		return self.env['report'].get_action(self, 'emsprime_core.report_student_list_by_course')
