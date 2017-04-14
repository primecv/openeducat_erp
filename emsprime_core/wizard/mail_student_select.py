# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017 Prime Consulting SA, Cape Verde (<http://prime.cv>).
#
##############################################################################

import base64
import logging
from email.utils import formataddr

import psycopg2

from openerp import _, api, fields, models
from openerp.exceptions import UserError
from openerp import tools
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException
from openerp.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)

class MailStudentSelectLine(models.TransientModel):
    _name = "mail.student.select.line"

    student_id = fields.Many2one('ems.student', 'Student')
    select_student = fields.Boolean('Select Student')
    wizard_id = fields.Many2one('mail.student.select', 'Wizard Id')


class MailStudentSelect(models.Model):
    _name = "mail.student.select"
    _inherit = ['mail.thread']
    _description = ""

    student_ids = fields.One2many('mail.student.select.line', 'wizard_id', 'Students')

    @api.multi
    def select_all(self):
        for rec in self:
            lineids = []
            temp = [lineids.append(l) for l in rec.student_ids]
            for ids in lineids:
                ids.write({'select_student': True})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.student.select',
                'target': 'new',
                'res_id': int(rec.id)
            }

    @api.multi
    def deselect_all(self):
        for rec in self:
            lineids = []
            temp = [lineids.append(l) for l in rec.student_ids]
            for ids in lineids:
                ids.write({'select_student': False})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.student.select',
                'target': 'new',
                'res_id': int(rec.id)
            }

    @api.multi
    def action_send_email(self):
        flag = False
        partners = []
        for rec in self:            
            for line in rec.student_ids:
                if line.select_student is True:
                    partners.append(line.student_id.partner_id.id)
                    flag = True
        if flag is False:
            raise UserError('Please select at least one student!')

        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('emsprime_core', 'email_compose_message_ems_classes_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': self._name,
            'default_res_id': self.ids[0],
            'default_use_template': False,
            'default_template_id': False,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_subject': 'ISCEE Notification',
            'default_body_html': '',
            'default_body': '',
            'default_partner_ids': [[6, 0, partners]],
            'default_message_type': 'email',
            'mass_mail_class_students': True,            
        })
        return {
            'name': 'Student Email Notification',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

class ComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.model
    def default_get(self, fields):
        """Set email subject
        """
        res = super(ComposeMessage, self).default_get(fields)
        context = self._context
        if 'mass_mail_class_students' in context:
            res.update({'subject': 'ISCEE Notification'})
        return res

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def send_get_mail_to(self, partner=None):
        """Forge the email_to with the following heuristic:
          - if 'partner', recipient specific (Partner Name <email>)
              - if email is being sent to Students from Classes, send email also at students institutional email address, if present.
          - else fallback on mail.email_to splitting """
        self.ensure_one()
        email_to = []
        if partner:
            context = self._context            
            if context and 'default_model' in context and context['default_model'] == 'mail.student.select':
                student = self.env['ems.student'].search([('partner_id','=',partner.id)])
                if student and student.institutional_email:
                    email_to.append(formataddr((partner.name, student.institutional_email)))
            email_to.append(formataddr((partner.name, partner.email)))
        else:
            email_to = tools.email_split_and_format(self.email_to)
        return email_to
