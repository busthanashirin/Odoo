# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import random
import string
from odoo.http import root


class ResCompany(models.Model):
    _inherit = 'res.company'

    msg91_auth_key = fields.Char(string='Auth Key')
    msg91_template_id = fields.Char(string='Template ID')
    msg91_otp = fields.Char('Otp')
