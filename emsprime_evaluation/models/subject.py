#-*- coding: utf-8 -*-

from openerp import models, api, fields

class EmsSubject(models.Model):
    _inherit = "ems.subject"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        """ filter Subjects on Ems Evaluation based on Faculty selected:
        """
        context = self._context or {}
        if context and 'filter_faculty_id' in context :
            faculty_id = context['filter_faculty_id']
            subjects = []
            if faculty_id:
                faculty = self.env['ems.faculty'].browse(faculty_id)
                for subject in faculty.faculty_subject_ids:
                    subjects.append(subject.id)
            args += [('id', 'in', subjects)]
        return super(EmsSubject, self).name_search(name, args, operator, limit)