# -*- coding: utf-8 -*-
import pdb
from datetime import date
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        _partner = request.env.user.partner_id

        name = _("No default access list")
        result = ""
        _generators = request.env['climbing_gym.access_list_generator'].sudo().search([('state', '=', 'active'), ('default_list', '=', 'true')])

        for generator in _generators:
            name = generator.name

            try:
                generator.validate_partner(_partner)
                result = _("All valid for this list")
            except ValidationError as e:
                result = _("Validation error: %s") % e.name

        values.update({
            'access_list_generator_name': name,
            'access_list_generator_result': result,

        })
        return values
