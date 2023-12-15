# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    salutation_id = fields.Selection([
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
        ('dr', 'Dr')
    ], 'Salutation', readonly=True, copy=False)
    user_login_mob_id = fields.Char(string='電話號碼')
    city = fields.Char(string='City', required=False)
    zip = fields.Char(string='Zip', required=False)
    referral_by = fields.Text(string='Referral By')


class ProductPriceListSetting(models.Model):
    _name = 'product.pricelist.setting'

    name = fields.Char(string="名稱")
    product_pricelist = fields.Many2one('product.pricelist', string="Price List")
