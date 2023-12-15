# -*- coding: utf-8 -*-

import logging
from odoo.http import request

from odoo.addons.portal.controllers import portal

_logger = logging.getLogger(__name__)


class WebsiteCustomerPortal(portal.CustomerPortal):

    OPTIONAL_BILLING_FIELDS = [*portal.CustomerPortal.OPTIONAL_BILLING_FIELDS, 'referral_by']

