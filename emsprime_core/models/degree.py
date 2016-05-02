# -*- coding: utf-8 -*-

from openerp import models, fields

class ems_course_degree(models.Model):
    _name = "ems.course.degree"
    _description = "Degrees"

    name = fields.Char(string="Degree Name", required=True)

