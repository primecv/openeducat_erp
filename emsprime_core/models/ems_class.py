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

    name = fields.Char('Class Name', size=64, required=True)
    faculty_id = fields.Many2one('ems.faculty', 'Faculty', required=True)
    subject_id = fields.Many2one('ems.subject', 'Subject', required=True)
    course_id = fields.Many2one('ems.course', 'Course', required=True)
    #student_ids = fields.Many2many('ems.student', string='Student(s)')
    enrollment_ids = fields.Many2many('ems.enrollment', string='Enrollment(s)')
    #semester_id = fields.Many2one('ems.semester', string='Semester')
    semester = fields.Selection([('I', 'I'), ('II', 'II')], 'Semester')
    #year = fields.Char('Year', size=4)
    academic_year = fields.Selection([('2016', '2016/2017'),('2015', '2015/2016'), ('2014', '2014/2015'),('2013', '2013/2014'),('2012', '2012/2013'), 
                                      ('2011', '2011/2012'), ('2010', '2010/2011'), ('2009', '2009/2010'), ('2008', '2008/2009'), ('2007', '2007/2008'),
									  ('2006', '2006/2007'), ('2005', '2005/2006'), ('2004', '2004/2005'), ('2003', '2003/2004'),('2002', '2002/2003'),
									  ('2001', '2001/2002'),('2000', '2000/2001'),('1999', '1999/2000'),('1998', '1998/1999'),('1997', '1997/1998'),
									  ('1996', '1996/1997'), ('1995', '1995/1996'),('1994', '1994/1995'),('1993', '1993/1994'),('1992', '1992/1993'),
									  ('1991', '1991/1992')
            ], 'Academic Year', track_visibility='onchange', required=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
