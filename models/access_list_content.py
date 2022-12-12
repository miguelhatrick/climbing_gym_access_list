# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import logging
import pytz

_logger = logging.getLogger(__name__)


class AccessListContent(models.Model):
    """Month event content"""
    _name = 'climbing_gym.access_list_content'
    _description = 'Access list content'
    _inherit = ['mail.thread']

    _sql_constraints = [
        ('partner_id_uniq', 'unique(access_list_id, partner_id)', "Can't inscribe the same contact twice!"),
    ]

    status_selection = [('pending', "Pending"), ('confirmed', "Confirmed"), ('cancel', "Cancelled")]

    name = fields.Char('Name', compute='_generate_name')
    partner_id = fields.Many2one('res.partner', string='Member', required=True, index=True, track_visibility=True)
    access_list_id = fields.Many2one('climbing_gym.access_list', string='Access List', required=True, track_visibility=True)
    state = fields.Selection(status_selection, 'Status', default='pending', track_visibility=True)

    @api.multi
    def action_pending(self):
        self.write({'state': 'pending'})

    @api.multi
    def action_confirm(self):
        _logger.info('Trying to confirm %s ...' % self.name)

        self.access_list_id.validate_partner(self.partner_id)
        self.write({'state': 'confirmed'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.onchange('state')
    def on_change_state(self):
        if self.state == 'confirmed':
            self.access_list_id.validate_partner(self.partner_id)

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    def _generate_name(self):
        # pdb.set_trace()
        for _map in self:
            _map.name = "ALC-%s" % (_map.id if _map.id else '')

    @api.onchange('access_list_id')
    def _onchange_access_list_id(self):

        """This disallows internal ID to be used on other member for the same membership"""
        if not self.partner_id or not self.access_list_id:
            return

        self.action_pending()

    @api.multi
    def unlink(self):
        for _content in self:
            if _content.access_list_id.state == 'closed':
                raise UserError(_('You cannot delete a content of a closed access list '))
        return super(AccessListContent, self).unlink()
