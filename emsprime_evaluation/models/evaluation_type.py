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

from openerp import models, fields


class EmsEvaluationType(models.Model):
    _name = 'ems.evaluation.type'

    name = fields.Char('Name', size=256, required=True)
    code = fields.Char('Code', size=4, required=True)
    parent_id = fields.Many2one('ems.evaluation.type', string='Parent')
    special = fields.Boolean('Special', default=False)
    report_title = fields.Char('Report Title', size=256)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
