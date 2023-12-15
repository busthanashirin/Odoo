# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class UserLogin(models.Model):
    _inherit = 'res.users'

    _sql_constraints = [
        # Partial constraint, complemented by a python constraint (see below).to check unique, login
        ('login_key', 'unique (user_login_mob, website_id)', 'You can not have two users with the same login ID!'),
    ]

    salutation = fields.Selection([
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
        ('dr', 'Dr')
    ], 'Salutation', copy=False, default='mr')
    user_login_mob = fields.Char('電話號碼', store=True, required=True)
    referral_by = fields.Text(string='Referral By')
    check_mail_verify = fields.Boolean(string='Check Mail Verification', default=False)

    @api.constrains('user_login_mob', 'website_id')
    def _check_login_id(self):
        """ Do not allow two users with the same login without website """
        self.partner_id.salutation_id = self.salutation
        self.partner_id.user_login_mob_id = self.user_login_mob
        self.partner_id.referral_by = self.referral_by
        self.flush_model(['user_login_mob', 'website_id'])
        self.env.cr.execute(
            """SELECT user_login_mob
                 FROM res_users
                WHERE user_login_mob IN (SELECT user_login_mob FROM res_users WHERE id IN %s AND website_id IS NULL)
                  AND website_id IS NULL
             GROUP BY user_login_mob
               HAVING COUNT(*) > 1
            """,
            (tuple(self.ids),)
        )
        if self.env.cr.rowcount:
            raise ValidationError(_('電話號碼已經被使用，請更改！'))

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.referral_by:
            res.partner_id.referral_by = res.referral_by
        return res
