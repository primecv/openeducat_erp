#-*- coding:utf-8 -*-

from openerp import fields, models, api
from openerp.exceptions import ValidationError
import xlrd
import base64

class ems_enrollment_import(models.TransientModel):
	_name = "ems.enrollment.import"
	_description = "Students Enrollment import through XLS"

	file = fields.Binary('File')
	name = fields.Char('Name')

	@api.multi	
	def load_inscription_subjects(self):
		inscriptions = self.env['ems.enrollment'].search([('type','=','I')])
		for insc in inscriptions:
			subjects = []
			subjectline = [subjects.append(i.id) for i in insc.subject_ids]
			for subject in subjects:
				course_id = insc.course_id.id
				course = self.env['ems.course.subject'].search([('subject_id','=',subject), ('course_id','=',course_id)])
				semester = course.semester
				vals = {'subject_id': subject, 'inscription_id': insc.id, 'semester': semester}
				self.env['ems.enrollment.inscription.subject'].create(vals)

	def do_import(self, cr, uid, ids, context=None):
		for rec in self.browse(cr, uid, ids):
			if not rec.file:
				raise ValidationError('Please select valid file.\nAllowed formats: csv, xls & xlsx.')
			else:
				filename = rec.name
			fileext = filename.split('.')[-1]

			if fileext not in ('xls', 'xlsx', 'csv'):
				raise ValidationError('Invalid / Unsupported File format.\nAllowed formats: csv, xls & xlsx.')

			if fileext in ('xls', 'xlsx'):
				try:
					data = base64.decodestring(rec.file)
					book = xlrd.open_workbook(file_contents = data)
					worksheet = book.sheet_names()
				except Exception,e:
					raise ValidationError('Invalid / Unsupported File format.\nPlease upload valid xls/xlsx file.\n%s\nTo see possible cause of this error, please check: https://github.com/hadley/readxl/issues/48'%(e))

				dup, total, success, fail = 0, 0, 0, 0
				for worksheet_name in [worksheet[0]]:
					worksheet = book.sheet_by_name(worksheet_name)
					num_rows = worksheet.nrows - 1
					num_cells = worksheet.ncols - 1
					for curr_row in range(1, num_rows + 1):
						total = total + 1
						curr_cell = -1
						result = []
						while curr_cell < num_cells:
							curr_cell += 1
							cell_value = worksheet.cell_value(curr_row, curr_cell)
							result.append(cell_value)
						if result:
							vals = {
								'roll_number': result[0],
								'type': 'M',
							}
							student_id, course_id, edition_id = False, False, False
							email = result[1]
							students = self.pool.get('ems.student').search(cr, uid, [('email','=',email.strip().lower())])
							if students:
								student_id = students[0]
								vals['student_id'] = student_id

							edition_code = result[4]
							editions = self.pool.get('ems.edition').search(cr, uid, [('code','=',edition_code.strip().upper())])
							if editions:
								edition_id = editions[0]
								vals['edition_id'] = edition_id
								course_id = self.pool.get('ems.edition').browse(cr, uid, [edition_id])[0].course_id.id
								vals['course_id'] = course_id
	
							if edition_id and student_id and course_id:
								exstudent = self.pool.get('ems.enrollment').search(cr, uid, [('student_id','=',vals['student_id']),('course_id','=',vals['course_id']),('edition_id','=',vals['edition_id'])])
								if exstudent:
									dup = dup + 1
								else:
									success = success + 1
									self.pool.get('ems.enrollment').create(cr, uid, vals)
							else: 
								fail = fail + 1
				print "Total : ", total
				print "Success : ", success
				print "Duplicates : ", dup
				print "Fail : ", fail
		return True
