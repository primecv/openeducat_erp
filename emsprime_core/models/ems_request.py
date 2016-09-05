# -*- coding: utf-8 -*-
###############################################################################
#
#    Prime Consulting SA
#    Copyright (C) 2016-TODAY Prime Consulting SA(<http://www.prime.cv>).
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
from datetime import datetime

class ems_request_type(models.Model):
    _name = 'ems.request.type'
    _description = "Request Type"

    name = fields.Char('Request Type', required=True)
    report_id = fields.Many2one('ir.actions.report.xml', 'Report')

class ems_request(models.Model):
    _name = "ems.request"
    _description = "Request"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    #JCF - 05-09-2016
    @api.one
    @api.depends('enrollment_id')
    def _get_curr_inscription(self):
        current_inscription_id = False
        enrollments = self.env['ems.enrollment'].search([('student_id','=',self.enrollment_id.student_id.id),('type','=','I')])
        print "Student:: "
        print self.enrollment_id.student_id.id
        #check current date with the latest enrollment edition:
        count = 0
        for enrollment in enrollments:
            try:
                if count == 0:
                    current_inscription_id = enrollment.id

                    start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                    count = count + 1
                else:
                    if start_date <= datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date() and enrollment.type=='I':
                        start_date = datetime.strptime(enrollment.edition_id.start_date, '%Y-%m-%d').date()
                        current_inscription_id = enrollment.id
            except Exception:
                pass

            self.current_inscription_id = current_inscription_id

    name = fields.Char('Request Name', required=True, track_visibility='onchange', select=True)
    student_id = fields.Many2one('ems.student', 'Student', track_visibility='onchange')
    enrollment_id = fields.Many2one('ems.enrollment', 'Record Number', track_visibility='onchange', select=True)
    request_type_id = fields.Many2one('ems.request.type', string='Request Type', track_visibility='onchange', select=True)
    description = fields.Text('Description')
    date = fields.Date('Request Date', track_visibility="onchange", default=fields.date.today(), readonly=True)
    state = fields.Selection(
        [('draft', 'New Request'), ('validate', 'Validated'),
         ('pending', 'Pending'), ('done', 'Done')],
        'State', default="draft", required=True, track_visibility='onchange', select=True)
    sequence = fields.Char('Sequence')
    current_inscription_id = fields.Many2one('ems.enrollment', string='Current Inscription', compute='_get_curr_inscription', store=True, track_visibility='onchange')

	
    def get_to_year(self, year):
        if year:
           return int(year) + 1
        return None

    @api.multi
    def action_validate(self):
        return self.write({'state':'validate'})

    @api.multi
    def action_pending(self):
        return self.write({'state':'pending'})

    @api.multi
    def action_print(self):
        """Generate sequence in "YYYY/0001" format by Request Type
        """
        year = datetime.now().date().year
        next_seq = str(year) + '/0001'
        self._cr.execute("""select sequence from ems_request where  sequence ilike '%s%%' order by id desc limit 1"""%(str(year) + '/'))
        result = self._cr.fetchone()
        if result:
            result = result[0]
            result = str(result).split('/')
        if result and len(result) == 2:
            result = int(result[1])
            next_seq = str(result + 1)
            while len(next_seq) < 4:
               next_seq = '0' + next_seq
            next_seq = str(year) + '/' + next_seq
        self.write({'state':'done', 'sequence':next_seq})
        return self.env['report'].get_action(self, self.request_type_id.report_id.report_name)

    @api.onchange('enrollment_id')
    def onchange_enrollment(self):
        student_name = ''
        enrollment_id = self.enrollment_id.id
        enrollments = self.env['ems.enrollment'].search([('id','=',enrollment_id)])
        for enrollment in enrollments:
            student_name=enrollment.student_id.complete_name
        self.name = student_name

    def get_academic_year(self, student_id):
        if student_id:
            academic_year = 0
            academic_year2 = 0
            str_academic_year=''
            enrollments = self.env['ems.enrollment'].search([('student_id','=',student_id),('type','=','I')], order="id desc", limit=1)
            for enrollment in enrollments:
                academic_year=enrollment.academic_year
                academic_year2 = int(academic_year) + 1
                str_academic_year = str(academic_year) + '/' + str(academic_year2)
            return str_academic_year
        return None

    def get_course_year(self, student_id):
        if student_id:
            course_year = 0
            enrollments = self.env['ems.enrollment'].search([('student_id','=',student_id),('type','=','I')], order="id desc", limit=1)
            for enrollment in enrollments:
                course_year=enrollment.course_year
            return course_year
        return None

