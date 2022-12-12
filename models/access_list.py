# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date, timezone
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .  import validate

class AccessList(models.Model):
    """List for accessing certain activities"""

    _name = 'climbing_gym.access_list'
    _description = 'List for accessing certain activities'
    _inherit = ['mail.thread']

    months_choices = []
    years_choices = []
    currentYear = datetime.now().year

    for i in range(1, 13):
        months_choices.append((i, date(currentYear, i, 1).strftime('%B')))

    for i in range(currentYear, currentYear + 5):
        years_choices.append((i, str(i)))

    status_selection = [('pending', "Pending"), ('closed', "Closed"), ('cancel', "Cancelled")]
    type_selection = [('public', "Public"), ('private', "Private")]

    name = fields.Char("Name", required=True)
    description = fields.Text(string='Description of the current template')

    access_list_contents_count = fields.Integer(compute='_compute_access_list_content__count')

    access_list_content_ids = fields.One2many('climbing_gym.access_list_content', inverse_name='access_list_id',
                                              string='Members', readonly=True)

    access_list_content_accepted_ids = fields.One2many('climbing_gym.access_list_content', string='Accepted students',
                                                       compute='_calculate_accepted_students_ids', readonly=True)

    require_medical_certificate = fields.Boolean(string="Require medical certificate", required=True)
    require_tags = fields.Many2many('res.partner.category', string='Required tags', track_visibility=True)
    require_memberships = fields.Many2many('climbing_gym.membership',
                                           string='Required membership',
                                           track_visibility=True)
    require_exams = fields.Many2many('climbing_gym_school.course_type', string='Required approved',
                                     track_visibility=True)

    location = fields.Many2one('res.partner', string='Access location', readonly=False, required=True)

    seats_availability = fields.Integer("Maximum Attendees", required=True)
    seats_available = fields.Integer("Available seats", compute='calculate_current_available_seats', readonly=True)

    event_type = fields.Selection(type_selection, 'Type', default='public')

    state = fields.Selection(status_selection, 'Status', default='pending')

    @api.multi
    def action_pending(self):
        self.write({'state': 'pending'})

    @api.multi
    def action_close(self):
        self.write({'state': 'closed'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    def calculate_current_available_seats(self):
        for em in self:
            em.seats_available = em.seats_availability - self.sudo().env[
                'climbing_gym.access_list_content'].search_count(
                [('access_list_id', '=', em.id), ('state', '=', 'approved')])

    @api.one
    def validate_partner(self, partner_id):
        validate.validate_partner(self, partner_id)

    def action_open_view_access_list_contents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Members',
            'view_mode': 'tree,form',
            'res_model': 'climbing_gym.access_list_content',
            'domain': [('access_list_id', '=', self.id)],
            # 'context': "{'create': False}"
        }

    @api.multi
    def _compute_access_list_content__count(self):
        for record in self:
            record.access_list_contents_count = self.env['climbing_gym.access_list_content'].search_count(
                [('access_list_id', '=', self.id)])

    def _calculate_accepted_students_ids(self):
        _filter = ['confirmed']
        for _c in self:
            _c.access_list_content_accepted_ids = _c.access_list_content_ids.search(
                [('access_list_id', '=', _c.id), ('state', 'in', _filter)])
