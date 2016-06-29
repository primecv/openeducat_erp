#-*- coding: utf-8 -*-

from openerp.osv import osv, fields

class ems_enrollment_inscricao_subject(osv.Model):
    _name = "ems.enrollment.inscricao.subject"
    _description = "Inscricao Subjects"

    _columns = {
		'name': fields.char('Name'),
		'subject_line': fields.one2many('ems.enrollment.inscricao.subject.line', 'form_id', 'Subjects'),
	}

    _defaults = {
		'name': 'Subjects'
	}

    def action_add_selected(self, cr, uid, ids, context=None):
        flag = False
        for rec in self.browse(cr, uid, ids):
            for inv in rec.subject_line:
                if inv.temp_check: flag = True
            if not flag:
                raise osv.except_osv(('Error!'), ('No Subject Selected!\nPlease select at least one Subject.'))
            subjects = []
            invs = [subjects.append(inv.subject_id.id) for inv in rec.subject_line if inv.temp_check is True]
            if context:
                model = context.get('active_model', False)
                res_id = context.get('active_id', False)
                print"##################                  ", model, res_id, subjects
                if model and res_id:
                    self.pool.get(model).write(cr, uid, [res_id], {'subject_ids': [[6,0,subjects]]})
            return True

    def action_add_all(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            subjects = []
            invs = [subjects.append(inv.subject_id.id) for inv in rec.subject_line]
            if context:
                model = context.get('active_model', False)
                res_id = context.get('active_id', False)
                if model and res_id:
                    self.pool.get(model).write(cr, uid, [res_id], {'subject_ids': [[6,0,subjects]]})
            return True

    def action_select_all(self, cr, uid, ids, context=None):
        subjects = []
        for rec in self.browse(cr, uid, ids):
            invs = [subjects.append(inv.id) for inv in rec.subject_line]
            self.pool.get('ems.enrollment.inscricao.subject.line').write(cr, uid, subjects, {'temp_check': True})
            return {
				'type': 'ir.actions.act_window',
				'res_model': self._name,
				'view_type': 'form',
				'view_mode': 'form',
				'context': context,
				'res_id': int(rec.id),
				'target': 'new'	
			}

    def action_deselect_all(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            for inv in rec.subject_line:
				self.pool.get('ems.enrollment.inscricao.subject.line').write(cr, uid, [inv.id], {'temp_check': False})
            return {
				'type': 'ir.actions.act_window',
				'res_model': self._name,
				'view_type': 'form',
				'view_mode': 'form',
				'context': context,
				'res_id': int(rec.id),
				'target': 'new'	
			}


class ems_enrollment_inscricao_subject_line(osv.Model):
	_name = "ems.enrollment.inscricao.subject.line"

	_columns = {
		'subject_id': fields.many2one('ems.subject', 'Subject'),
		'form_id': fields.many2one('ems.enrollment.inscricao.subject', 'Form Id'),
		'temp_check': fields.boolean('Add/Remove'),
	}
