# -*- coding: utf-8 -*-
from odoo.addons.auth_signup.models.res_users import SignupError
from werkzeug.urls import url_encode

import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi

import logging
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
import requests
import re

from odoo import http, _
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.http import request
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class SignupLogin(Home):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        qcontext["user_login_mob"] = kw.get('user_login_mob')
        qcontext["salutation"] = kw.get('salutation')
        qcontext["referral_by"] = kw.get('referral_by')

        email = kw.get('login')
        pattern = r'^[a-z0-9]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if email:
            if not re.match(pattern, email):
                qcontext["error"] = _("Email Format is not correct")

        phone = kw.get('user_login_mob')
        pattern = re.compile(r'^\d{8}$')
        if phone:
            if not pattern.match(phone):
                qcontext["error"] = _("Phone Number is not correct")

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                product_price_setting = request.env['product.pricelist.setting'].sudo().search([], limit=1)
                logging.info('product_price_setting:' + str(product_price_setting))
                if product_price_setting:
                    logging.info('product_price_setting[0].product_pricelist:' + str(product_price_setting[0].product_pricelist))
                    user_sudo.partner_id.property_product_pricelist = product_price_setting[0].product_pricelist
                user_sudo.partner_id.user_login_mob_id = str(user_sudo.user_login_mob)
                user_sudo.partner_id.phone = str(user_sudo.user_login_mob)
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                           raise_if_not_found=False)
                template1 = request.env.ref('login_id.send_verification_email',
                                            raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                if user_sudo and template1:
                    template1.sudo().send_mail(user_sudo.id, force_send=True)
                if user_sudo.check_mail_verify:
                    return self.web_login(*args, **kw)
                else:
                    qcontext["error"] = _("Please verify the given Email first")
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                elif request.env["res.users"].sudo().search(
                        [("user_login_mob", "=", qcontext.get("user_login_mob"))]):
                    qcontext["error"] = _("Another user is already registered using this Login ID.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search(
                [('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user and user.check_mail_verify:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    def _prepare_signup_values(self, qcontext):
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'salutation', 'user_login_mob', 'referral_by')}
        # values['portal_users'] = False
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported_lang_codes:
            values['lang'] = lang
        return values

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        if kw.get('user_login_mob') is None:
            return super().web_login(redirect=None, **kw)
        user = request.env['res.users'].sudo().search(['|', ('login', '=', kw.get('user_login_mob')),
                                                       ('user_login_mob', '=', kw.get('user_login_mob'))])
        if user:
            request.params['login'] = user.login
        if not user.check_mail_verify:
            response = request.render('login_id.verification_mail', {'user': user})
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
            return response

        return super().web_login(redirect=None, **kw)

    @http.route('/web/send_sms', auth='public', type='json')
    def web_sms_otp(self, **kw):
        phone = kw.get('country_code') + kw.get('phone')
        template_id = request.env.company.msg91_template_id
        authkey = request.env.company.msg91_auth_key
        otp = kw.get('otp')

        url = "https://control.msg91.com/api/v5/otp?mobile=%s&template_id=%s" % (phone, template_id)

        payload = {
            "Param1": otp,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authkey": authkey
        }
        response = requests.post(url, json=payload, headers=headers)

    @http.route('/web/verify_email', auth='public')
    def web_check_verify_email(self, *args, **kw):
        user_id = int(kw.get('value_param'))
        user = request.env['res.users'].sudo().browse(user_id)
        user.check_mail_verify = True
        return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

    @http.route('/web/send_verify_email', auth='public')
    def web_verify_email(self, *args, **kw):
        mail = kw.get('login_mail')
        user = request.env['res.users'].sudo().search([('login', '=', mail)])
        template = request.env.ref('login_id.send_verification_email', raise_if_not_found=False)
        if user and template:
            template.sudo().send_mail(user.id, force_send=True)
        return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))
