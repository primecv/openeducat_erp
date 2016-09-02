#-*- coding:utf-8 -*-

from openerp import fields, models, api
from openerp.exceptions import ValidationError
import xlrd
import base64
import logging

_logger = logging.getLogger(__name__)

class ems_enrollment_import(models.TransientModel):
	_name = "ems.enrollment.import"
	_description = "Students Enrollment import through XLS"

	file = fields.Binary('File')
	name = fields.Char('Name')
	type = fields.Selection([('e','Matricula Enrollment'),('g', 'Inscription Grades')], 'Type', help="Matricula Enrollment: To Import Matricula Enrollments\nInscription Grades: To update Grades on Inscription Enrollment Subjects")

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
					total_rows, invalid_row, no_student_exists, no_subject_exists, grade_import, grade_update = 0,0,0,0,0,0
					for curr_row in range(1, num_rows + 1):
						total_rows = total_rows + 1
						curr_cell = -1
						result = []
						while curr_cell < num_cells:
							curr_cell += 1
							cell_value = worksheet.cell_value(curr_row, curr_cell)
							result.append(cell_value)
						if rec.type == 'g':#Inscription Subjects Grade Update
							flag = False
							if result:
								if result[7] and isinstance(result[7], (int, long, float)):
									flag = True
								elif result[7]:
									try:
										result[7] = int(result[7])
										flag = True
									except Exception:
										pass
									
							if result and result[3] and result[6] and flag:
								total = total + 1
								try:
									student_code = str(result[3]).strip()
								except Exception:
									student_code = str(result[3].encode('utf-8')).strip()
								try:
									subject_code = str(result[6]).strip()
								except Exception:
									subject_code = str(result[6].encode('utf-8')).strip()
								try:
									year = str(result[1]).strip()
								except Exception:
									year = str(result[1].encode('utf-8')).strip()
								year = year.split('/')[0]
								grade = result[7]

								student_id = self.pool.get('ems.student').search(cr, uid, [('roll_number','=',student_code)])
								if student_id: 
									student_id = student_id[0]
									subject_id = self.pool.get('ems.subject').search(cr, uid, [('code','=',subject_code)])
									if subject_id: 
										subject_id = subject_id[0]
									if subject_id:
										enrollment_ids = self.pool.get('ems.enrollment').search(cr, uid, [
															('student_id','=',student_id),
															('type','=','I'), ('state','=','draft')])
										subject_line_id = self.pool.get('ems.enrollment.inscription.subject').search(cr, uid, [
															('inscription_id','in',enrollment_ids),
															('subject_id','=',subject_id)], order="id desc", limit=1)
										if len(subject_line_id) == 1:
											grade_update = grade_update + 1
											self.pool.get('ems.enrollment.inscription.subject').write(cr, uid, subject_line_id,
															{'grade': grade})
										else:#create new Grades entry
											grade_id = 0
											edition_id = 0
											course_id = 0
											for student in self.pool.get('ems.student').browse(cr, uid, [student_id]):
												for inscription in student.roll_number_line:
													if inscription.type == 'I':
														insc_year = inscription.roll_number and str(inscription.roll_number).split('.')
														if insc_year:
															insc_year = insc_year[-1]
															if insc_year == year:
																grade_id = inscription.id
																course_id = inscription.course_id.id
																edition_id = inscription.edition_id.id
																break
												if grade_id:
													vals = {}
													vals['inscription_id'] = grade_id
													vals['course_id'] = course_id
													vals['edition_id'] = edition_id
													vals['subject_id'] = subject_id
													vals['grade'] = grade
													ems_edition_subject_id = self.pool.get('ems.edition.subject').search(cr, uid, [('subject_id','=',subject_id),('edition_id','=',edition_id)])
													if ems_edition_subject_id:
														for eds in self.pool.get('ems.edition.subject').browse(cr,uid,ems_edition_subject_id):
															
															vals['semester'] = eds.semester
															vals['ect'] = eds.ects
															vals['semester_copy'] = eds.semester
															vals['ect_copy'] = eds.ects

													self.pool.get('ems.enrollment.inscription.subject').create(cr,uid,vals)
													grade_import = grade_import + 1
									else:
											no_subject_exists = no_subject_exists + 1
								else:
									no_student_exists = no_student_exists + 1
							else:
								invalid_row = invalid_row + 1
						if rec.type == 'e':#Matricula Enrollment Import
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
									total = total + 1
									exstudent = self.pool.get('ems.enrollment').search(cr, uid, [('student_id','=',vals['student_id']),('course_id','=',vals['course_id']),('edition_id','=',vals['edition_id'])])
									if exstudent:
										dup = dup + 1
									else:
										success = success + 1
										self.pool.get('ems.enrollment').create(cr, uid, vals)
								else: 
									fail = fail + 1
					if rec.type == 'g':
						_logger.info("Import Grades Script has started. File - %s"%(filename))
						_logger.info("Total Rows in File : %s"%(str(total_rows)))
						msg = "Invalid Rows : %s\n"%(str(invalid_row))
						msg = msg + "Student do not exists. Number of Rows : %s\n"%(str(no_student_exists))
						msg = msg + "Subject do not exists. Number of Rows : %s\n"%(str(no_subject_exists))
						msg = msg + "Grades Updated on Existing Inscription Subjects : %s\n"%(str(grade_update))
						msg = msg + "New Grades Imported on Existing Inscriptions : %s"%(str(grade_import))
						_logger.info(msg)
				print "Total : ", total
				print "Success : ", success
				print "Duplicates : ", dup
				print "Fail : ", fail
		return True
