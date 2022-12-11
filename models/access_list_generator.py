# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccessListGenerator(models.Model):
    """Generator for access list"""
    _name = 'climbing_gym.access_list_generator'
    _description = 'List for accessing certain activities'
    _inherit = ['mail.thread']

    days_choices = []
    status_selection = [('pending', "Pending"), ('active', "Active"), ('cancel', "Cancelled")]
    type_selection = [('public', "Public"), ('private', "Private")]
    for i in range(1, 28):
        days_choices.append((i, i))

    name = fields.Char("Name", required=True)
    description = fields.Text(string='Description of the current template')
    require_medical_certificate = fields.Boolean(string="Require medical certificate", required=True)
    require_tags = fields.Many2many('res.partner.category', string='Required tags', track_visibility=True)
    require_memberships = fields.Many2many(
        string='Required membership',
        track_visibility=True,
        comodel_name='climbing_gym.membership',
        relation='access_list_generator_l',
        column1='alg_id',
        column2='mm_id',
    )

    require_exams = fields.Many2many(
        string='Required approved',
        track_visibility=True,
        comodel_name='climbing_gym_school.course_type',
        relation='access_list_generator_c',
        column1='alg_id',
        column2='co_id',
    )

    location = fields.Many2one('res.partner', string='Access location', readonly=False, required=True)
    seats_availability = fields.Integer("Maximum Attendees", required=True, default=500)
    process_day = fields.Selection(days_choices, "Day of the month where the cron job runs", required=True, default=26)
    event_type = fields.Selection(type_selection, 'Type', default='public')
    state = fields.Selection(status_selection, 'Status', default='pending')

    @api.multi
    def action_pending(self):
        self.write({'state': 'pending'})

    @api.multi
    def action_active(self):
        self.write({'state': 'active'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    def action_generate_by_tag(self):
        raise NotImplementedError

    def _get_generator_name(self):
        return "%s - %s" % (
            datetime.now().strftime("%Y-%m-%d"),
            self.name)

    def generate_access_list(self):
        # Find all with valid memberships
        _logger.info('Generating new access list: %s' % self.name)

        active_memberships = self.env['climbing_gym.member_membership'].sudo().search(
            [('state', '=', 'active'), ('membership_id', 'in', self.require_memberships.ids)])

        partner_ids = list(map(lambda x: x.partner_id, active_memberships))
        partner_ids = list(set(partner_ids))

        # create access list
        _access_list = self.env['climbing_gym.access_list']
        _access_list_content = self.env['climbing_gym.access_list_content']

        _access_list_id = _access_list.create({
            'name': self._get_generator_name(),
            'description': self.description,
            'require_medical_certificate': self.require_medical_certificate,
            'require_tags': self.require_tags,
            'require_memberships': [(6, 0, self.require_memberships.ids)],
            'require_exams': [(6, 0, self.require_exams.ids)],
            'location': self.location.id,
            'seats_availability': self.seats_availability,
            'event_type': self.event_type,
            'state': 'pending'
        })

        # Validate and add contacts
        for partner_id in partner_ids:

            try:
                _access_list_id.validate_partner(partner_id)
                _content_id = _access_list_content.create({
                    'partner_id': partner_id.id,
                    'access_list_id': _access_list_id.id,
                    'state': 'confirmed',
                })

                # add the event
                _access_list_id.access_list_content_ids = [(4, _content_id.id)]
            except ValidationError as e:
                _logger.info("Partner %s cant be added %s" % (partner_id.name, e))

        return _access_list_id

    def action_generate(self):
        _access_list = self.generate_access_list()
        return self.action_open_form_access_list(_access_list)

    def action_open_form_access_list(self, access_list):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Access list',
            'view_mode': 'form',
            'res_model': 'climbing_gym.access_list',
            'res_id': access_list.id,
        }
