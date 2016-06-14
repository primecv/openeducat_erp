#-*- coding:utf-8 -*-

from openerp.osv import osv, fields
from email.utils import formataddr
from openerp import SUPERUSER_ID, api

class mail_message(osv.Model):
	_inherit = 'mail.message'

	def _get_default_from(self, cr, uid, context=None):
		this = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
		if this.alias_name and this.alias_domain:
			return formataddr((this.name, '%s@%s' % (this.alias_name, this.alias_domain)))
		elif this.email:
			return formataddr((this.name, this.email))
		else:
			return formataddr((this.company_id.name, this.company_id.partner_id.email))
		raise osv.except_osv(_('Invalid Action!'), _("Unable to send email, please configure the sender's email address or alias."))
	
	_defaults = {
        'email_from': lambda self, cr, uid, ctx=None: self._get_default_from(cr, uid, ctx),
	}

