import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class Users(http.Controller):
    """To create new user"""

    @http.route('/user/login', type='json', auth='public', csrf=False, methods=['POST'])
    def user_login(self, **kw):
        try:
            users = request.env['res.users'].with_user(1).search([])
            for user in users:
                if not user.user_login_mob:
                    user.user_login_mob = user.login

        except Exception as e:
            _logger.error("%s" % str(e))