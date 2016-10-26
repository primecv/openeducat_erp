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

class EmsClass(models.Model):
    _name = 'ems.class'

    @api.one
    @api.constrains('year')
    def _check_year(self):
        for year in self.year:
           if ord(year) not in (48, 49, 50, 51, 52, 53, 54, 55, 56, 57):
               raise ValidationError(_("Invalid Year!\n\nYear must be between 2000 - 3000"))
        if int(self.year) > 3000 or int(self.year) < 2000:
           raise ValidationError(_("Invalid Date!"))

    @api.onchange('course_id')
    def onchange_course(self):
        self.edition_id = False
        self.subject_id = False

    @api.onchange('edition_id')
    def onchange_edition(self):
        self.subject_id = False

    @api.onchange('academic_year', 'subject_id')
    def onchange_subject_academic_year(self):
        self.enrollment_ids = False

    name = fields.Char('Class Name', size=64, required=True)
    faculty_id = fields.Many2one('ems.faculty', 'Faculty', required=True)
    subject_id = fields.Many2one('ems.subject', 'Subject', required=True)
    course_id = fields.Many2one('ems.course', 'Course', required=False)
    edition_id = fields.Many2one('ems.edition', 'Edition')
    student_ids = fields.Many2many('ems.student', string='Student(s)')
    enrollment_ids = fields.Many2many('ems.enrollment', string='Enrollment(s)')
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

    @api.multi
    def load_inscriptions(self):        
        for eclass in self:
            select_clause = "select e.id from ems_enrollment e, ems_subject s, ems_enrollment_inscription_subject eis, ems_edition ed, ems_university_center univ "
            where_clause = """ where e.id=eis.inscription_id and
                            eis.subject_id=s.id and
                            e.edition_id = ed.id and
                            ed.university_center_id = univ.id and
                            univ.id = %s and
                            e.academic_year is not null and
                            e.academic_year='%s'"""%(eclass.university_center_id.id, eclass.academic_year)
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
            if res:
                self.write({'enrollment_ids': [[6,0, res]]})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
