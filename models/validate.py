# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


def validate_partner(access_list_type, partner_id):
    """Validate if a partner has all the prerequisites to be allowed in this access list"""
    if not partner_id:
        raise ValidationError(_("Can't confirm without a valid partner"))

    member_memberships_ids = partner_id.climbing_gym_member_membership_ids

    # Valid membership
    if access_list_type.require_memberships:
        if not member_memberships_ids.filtered(
                lambda a: a.state == 'active' and a.membership_id in access_list_type.require_memberships):
            raise ValidationError(_("No active valid Membership"))

    # Valid medical certificate
    if access_list_type.require_medical_certificate:
        if not partner_id.climbing_gym_medical_certificate_valid:
            raise ValidationError(_("Medical certificate is not valid"))

    # Valid tags
    for _tag in access_list_type.require_tags:
        if _tag not in partner_id.category_id:
            raise ValidationError(_("Partner has not the required tags!"))

    # Valid exams
    for _course_type_id in access_list_type.require_exams:
        if not partner_id.climbing_gym_school_exam_student_ids.filtered(
                lambda e: e.course_id.course_type_id == _course_type_id and e.state == 'approved'):
            raise ValidationError(_("Partner has not approved the required course!"))
