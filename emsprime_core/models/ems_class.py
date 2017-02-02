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

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.tools.translate import _
from datetime import datetime, date

class EmsClass(models.Model):
    _name = 'ems.class'

    @api.multi
    def action_load_enrollments(self):
        """Load related enrollments
        """
        class_ids = self.env['ems.class'].search([('id','>',0)])

        for eclass in class_ids:
            class_id=eclass.id
            self._cr.execute("""select ems_enrollment_id from ems_class_ems_enrollment_rel WHERE ems_class_id=%s"""%(class_id))
            result = self._cr.fetchall()

            for res in result:
                enrollment_id=res[0]
                self.env['ems.class.enrollment'].create({
                    'class_id': class_id,
                    'enrollment_id': enrollment_id,
                    'evaluation_type': 'continuous'
                })
	
    def compute_class_name(self, subject_id=False, faculty_id=False, academic_year=False, class_id=False):
        faculty_code = 'FACULTY'
        subject_code = 'SUB'
        if class_id:
            if not faculty_id:
                faculty_id = class_id.faculty_id.id
            if not subject_id:
                subject_id = class_id.subject_id.id
            if not academic_year:
                academic_year = class_id.academic_year
        if faculty_id:
            faculty = self.env['ems.faculty'].browse([faculty_id])
            if faculty.code:
                faculty_code = str(faculty.code)
        if subject_id:
            subject = self.env['ems.subject'].browse([subject_id])
            if subject.code:
                subject_code = str(subject.code)
        year = str(date.today().year)
        res = self.search([('subject_id','=',subject_id), ('faculty_id','=',faculty_id),('academic_year','=',academic_year)])
        class_count = res and str(len(res) + 1) or '1'
        name = '.'.join([faculty_code, subject_code, year, class_count])
        return name

    @api.one
    @api.constrains('year')
    def _check_year(self):
        for year in self.year:
           if ord(year) not in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57):
               raise ValidationError(_("Invalid Year!\n\nYear must be between 2000 - 3000"))
        if int(self.year) > 3000 or int(self.year) < 2000:
           raise ValidationError(_("Invalid Date!"))


    '''@api.onchange('course_id')
    def onchange_course(self):
        self.edition_id = False
        self.subject_id = False

    @api.onchange('edition_id')
    def onchange_edition(self):
        self.subject_id = False'''

    @api.onchange('academic_year', 'subject_id')
    def onchange_subject_academic_year(self):
        #self.enrollment_ids = False
        self.enrollment_line = False

    name = fields.Char('Class Name', size=64, readonly=True)
    faculty_id = fields.Many2one('ems.faculty', 'Faculty', required=True)
    subject_id = fields.Many2one('ems.subject', 'Subject', required=True)
    course_id = fields.Many2one('ems.course', 'Course', required=False)
    edition_id = fields.Many2one('ems.edition', 'Edition')
    student_ids = fields.Many2many('ems.student', string='Student(s)')
    enrollment_ids = fields.Many2many('ems.enrollment', string='Enrollment(s)', copy=False)
    #semester_id = fields.Many2one('ems.semester', string='Semester')
    semester = fields.Selection([('I', 'I'), ('II', 'II')], 'Semester')
    year = fields.Char('Year', size=4)
    academic_year = fields.Selection([('2016', '2016/2017'),('2015', '2015/2016'), ('2014', '2014/2015'),('2013', '2013/2014'),('2012', '2012/2013'), 
                                      ('2011', '2011/2012'), ('2010', '2010/2011'), ('2009', '2009/2010'), ('2008', '2008/2009'), ('2007', '2007/2008'),
									  ('2006', '2006/2007'), ('2005', '2005/2006'), ('2004', '2004/2005'), ('2003', '2003/2004'),('2002', '2002/2003'),
									  ('2001', '2001/2002'),('2000', '2000/2001'),('1999', '1999/2000'),('1998', '1998/1999'),('1997', '1997/1998'),
									  ('1996', '1996/1997'), ('1995', '1995/1996'),('1994', '1994/1995'),('1993', '1993/1994'),('1992', '1992/1993'),
									  ('1991', '1991/1992')
            ], 'Academic Year', track_visibility='onchange', required=True)
    university_center_id = fields.Many2one('ems.university.center', 'University Center')
    course_year = fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], 'Course Year',
                     track_visibility='onchange')
    enrollment_line = fields.One2many(
        'ems.class.enrollment', 'class_id', 'Enrollments')

    @api.model
    def create(self, vals):
    	academic_year = vals.get('academic_year', False)
    	subject_id = vals.get('subject_id', False)
    	faculty_id = vals.get('faculty_id', False)
    	vals['name'] = self.compute_class_name(subject_id, faculty_id, academic_year)
        return super(EmsClass, self).create(vals)

    @api.multi
    def write(self, vals):
        subject = self.subject_id.id
        faculty = self.faculty_id.id
        academic_year = self.academic_year
        if 'subject_id' in vals:
            subject = vals['subject_id']
        if 'faculty_id' in vals:
            faculty = vals['faculty_id']
        if 'academic_year' in vals:
            academic_year = vals['academic_year']
        if ('subject_id' in vals) or ('faculty_id' in vals) or ('academic_year' in vals):
            name = self.compute_class_name(subject, faculty, academic_year)
            vals['name'] = name
        return super(EmsClass, self).write(vals)

    @api.multi
    def load_inscriptions(self):        
        academic_year = self.academic_year
        university_center_id = self.university_center_id.id
        subject_id = self.subject_id.id
        existing_enrollments = []
        existing_classes = self.search([('academic_year', '=', academic_year), 
                                        ('subject_id', '=', subject_id), 
                                        ('university_center_id', '=', university_center_id),
                                        ('id', '!=', self.id)
                                        ])
        line_ids = []
        for e_class in existing_classes:
            for enrollment in e_class.enrollment_line:
                existing_enrollments.append(enrollment.id)
        for eclass in self:
            outer_select = """select v.id from ("""
            if eclass.course_id:
                select_clause = """select e.id,(select last_subject_enrollment('%s',%s,%s,%s,e.student_id,e.id)) as last_enrollment from ems_enrollment e, ems_subject s, ems_enrollment_inscription_subject eis, ems_edition ed, ems_university_center univ, ems_student st"""%(eclass.academic_year,eclass.university_center_id.id,eclass.subject_id.id,eclass.course_id.id)
            else:
                select_clause = """select e.id,(select last_subject_enrollment_no_course('%s',%s,%s,e.student_id,e.id)) as last_enrollment from ems_enrollment e, ems_subject s, ems_enrollment_inscription_subject eis, ems_edition ed, ems_university_center univ, ems_student st"""%(eclass.academic_year,eclass.university_center_id.id,eclass.subject_id.id)
            where_clause = """ where e.id=eis.inscription_id and
                            eis.subject_id=s.id and
                            e.edition_id = ed.id and
                            ed.university_center_id = univ.id and
							e.student_id=st.id and
                            univ.id = %s and
                            e.academic_year is not null and
                            e.academic_year='%s' and 
							(eis.grade < 10 or eis.grade is null) and
							(eis.equivalence is false or eis.equivalence is null) and
							st.active=true and
                            eis.subject_id=%s"""%(eclass.university_center_id.id, eclass.academic_year, eclass.subject_id.id)
            close_select = """) v where v.last_enrollment is true"""
            if eclass.course_id:
                where_clause += ' and e.course_id=%s'%(eclass.course_id.id)
            if eclass.edition_id:
                where_clause += ' and e.edition_id=%s'%(eclass.edition_id.id)

            query = outer_select + select_clause + where_clause + close_select
            self._cr.execute(query)
            result = self._cr.fetchall()
            res = []
            for r in result:
                r = list(r)
                res.append(r[0])
            for enrollment in self.enrollment_line:
                 res.append(enrollment.id)
            new_enrollments = []
            for enrollment in res:
                if enrollment not in existing_enrollments:
                    new_enrollments.append(enrollment)
            if new_enrollments:
                for enroll in new_enrollments:
                    line_ids.append([0, False,{'class_id': self.id,'enrollment_id': enroll}])
        self.enrollment_line = line_ids

    '''def load_inscriptions(self):        
        academic_year = self.academic_year
        university_center_id = self.university_center_id.id
        subject_id = self.subject_id.id
        existing_enrollments = []
        existing_classes = self.search([('academic_year', '=', academic_year), 
                                        ('subject_id', '=', subject_id), 
                                        ('university_center_id', '=', university_center_id),
                                        ('id', '!=', self.id)
                                        ])
        for e_class in existing_classes:
            for enrollment in e_class.enrollment_ids:
                existing_enrollments.append(enrollment.id)
        for eclass in self:
            select_clause = "select e.id from ems_enrollment e, ems_subject s, ems_enrollment_inscription_subject eis, ems_edition ed, ems_university_center univ "
            where_clause = """ where e.id=eis.inscription_id and
                            eis.subject_id=s.id and
                            e.edition_id = ed.id and
                            ed.university_center_id = univ.id and
                            univ.id = %s and
                            e.academic_year is not null and
                            e.academic_year='%s' and 
							(eis.grade < 10 or eis.grade is null) and
                            eis.subject_id=%s"""%(eclass.university_center_id.id, eclass.academic_year, eclass.subject_id.id)
            if eclass.course_id:
                where_clause += ' and e.course_id=%s'%(eclass.course_id.id)
            if eclass.edition_id:
                where_clause += ' and e.edition_id=%s'%(eclass.edition_id.id)

            query = select_clause + where_clause
            self._cr.execute(query)
            result = self._cr.fetchall()
            res = []
            for r in result:
                r = list(r)
                res.append(r[0])
            for enrollment in self.enrollment_ids:
                 res.append(enrollment.id)
            new_enrollments = []
            for enrollment in res:
                if enrollment not in existing_enrollments:
                    new_enrollments.append(enrollment)
            if new_enrollments:
                self.write({'enrollment_ids': [[6,0, new_enrollments]]})'''

    def init(self, cr):
        cr.execute("""
CREATE OR REPLACE FUNCTION last_subject_enrollment(character varying, integer, integer, integer, integer, integer)
 RETURNS boolean AS
$BODY$ declare                                                                                                                                                                                                                                                                  
                 v_enrollment integer;                                                                                                      
                                                                                                                                            
  begin                                                                                                                                     
				select e.id into v_enrollment
				from ems_enrollment e,ems_subject s,ems_enrollment_inscription_subject eis, ems_edition ed, ems_university_center univ, ems_student st
				where e.id=eis.inscription_id
				and eis.subject_id=s.id
				and e.edition_id = ed.id
				and ed.university_center_id = univ.id
				and e.student_id=st.id
				and univ.id =$2
				and e.academic_year is not null
				and e.academic_year=$1
				and (eis.grade < 10 or eis.grade is null)
				and (eis.equivalence is false or eis.equivalence is null)
				and st.active=true
				and eis.subject_id=$3 
				and e.course_id=$4
				and e.student_id=$5
				order by e.roll_number desc
				limit 1;

				IF v_enrollment=$6 THEN 
					return TRUE; 
				ELSE
					RETURN FALSE;
				END IF;
				
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
            """)

        cr.execute("""
CREATE OR REPLACE FUNCTION last_subject_enrollment_no_course(character varying, integer, integer, integer, integer)
 RETURNS boolean AS
$BODY$ declare                                                                                                                                                                                                                                                                  
                 v_enrollment integer;                                                                                                      
                                                                                                                                            
  begin                                                                                                                                     
				select e.id into v_enrollment
				from ems_enrollment e,ems_subject s,ems_enrollment_inscription_subject eis, ems_edition ed, ems_university_center univ, ems_student st
				where e.id=eis.inscription_id
				and eis.subject_id=s.id
				and e.edition_id = ed.id
				and ed.university_center_id = univ.id
				and e.student_id=st.id
				and univ.id =$2
				and e.academic_year is not null
				and e.academic_year=$1
				and (eis.grade < 10 or eis.grade is null)
				and (eis.equivalence is false or eis.equivalence is null)
				and st.active=true
				and eis.subject_id=$3 
				and e.student_id=$4
				order by e.roll_number desc
				limit 1;

				IF v_enrollment=$5 THEN 
					return TRUE; 
				ELSE
					RETURN FALSE;
				END IF;
				
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
            """)

class EmsClassEnrollments(models.Model):
    _name = "ems.class.enrollment"
    _description = "Class Students"
    _rec_name = "enrollment_id"
    _order = "student_roll_number"

    class_id = fields.Many2one('ems.class', string='Class')
    enrollment_id = fields.Many2one('ems.enrollment', string='Inscription Enrollment')
    student_roll_number = fields.Char(related='enrollment_id.roll_number', string='Roll number', store=True)
    course_id = fields.Many2one('ems.course', related="enrollment_id.course_id", string='Course', store=True, readonly=True)
    edition_id = fields.Many2one('ems.edition', related="enrollment_id.edition_id", string='Edition', store=True, readonly=True)
    student_id = fields.Many2one('ems.student', related="enrollment_id.student_id", string='Student', store=True, readonly=True)
    evaluation_type = fields.Selection([('continuous', 'Continuous'), ('regular_exam', 'Regular Exam')], 'Evaluation Type', default='continuous')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
