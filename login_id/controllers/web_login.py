# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class WebLogin(WebsiteSale):

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        logging.info('add new address start.')
        res = super().address(**kw)
        partner_id = int(kw.get('partner_id', -1))
        logging.info('add new address partner_id.' + str(partner_id))
        if partner_id > -1:
            partner = request.env['res.partner'].sudo().browse(partner_id)
            if kw.get('salutation_id'):
                partner.salutation_id = kw.get('salutation_id')
            if kw.get('user_login_mob_id'):
                partner.user_login_mob_id = kw.get('user_login_mob_id')
        return res
