# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command, _, tools
from odoo.tools import email_normalize
from odoo.exceptions import ValidationError

class PortalWizardInherit(models.TransientModel):
    _inherit = 'portal.wizard'

    @api.depends('partner_ids')
    def _compute_user_ids(self):
        for portal_wizard in self:
            portal_wizard.user_ids = [
                Command.create({
                    'partner_id': partner.id,
                    'email': partner.email,
                    'user_login_id': partner.user_login_mob_id or '',
                })
                for partner in portal_wizard.partner_ids
            ]


class PortalUserLogin(models.TransientModel):
    _inherit = 'portal.wizard.user'

    user_login_id = fields.Char('Login ID', required=True)
    def action_grant_access(self):
        res = super(PortalUserLogin, self).action_grant_access()
        if self.partner_id.user_login_mob_id != self.user_login_id:
            self.partner_id.write({'user_login_mob_id': self.user_login_id})

        return res

    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        vals = self.env['res.users'].sudo().search([('user_login_mob', '=', self.user_login_id)])
        if vals:
            raise ValidationError(_('You can not have two users with the same loginID!'))
        else:
            return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
                'email': email_normalize(self.email),
                'login': email_normalize(self.email),
                'user_login_mob': self.user_login_id,
                'partner_id': self.partner_id.id,
                'company_id': self.env.company.id,
                'company_ids': [(6, 0, self.env.company.ids)],
                # 'portal_users': True
            })
