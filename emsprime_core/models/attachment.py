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


class EmsAttachment(models.Model):
    _name = 'ems.attachment'
    _rec_name = 'attachment_type_id'

    dates_fname = fields.Char('Filename', size=100, required=True)
    attachment_type_id = fields.Many2one('ems.attachment.type', 'Type', required=True)
    attachment = fields.binary('Type')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
