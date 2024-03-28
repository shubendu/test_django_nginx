"""
Contains utility functions for the inspections app.
"""
import logging
import pdfkit
from config_app.utils import get_domain, get_protocol
from django.conf import settings
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.template.loader import get_template
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from inspection_template.models import InspectionTemplateProfile, validate_email_list
from inspections.models import Inspection
from inspections.mixins import InspectionContextMixin

logger = logging.getLogger(__name__)
User = get_user_model()


def date_as_str(date_obj):
    return date_obj.strftime("%Y-%m-%d")


def get_reg_no(inspection_obj):
    reg_no = None
    try:
        reg_no = inspection_obj.inspection_item.ref
    except Exception:
        reg_no = "reg-no"
    return reg_no


def report_name(inspection_obj):
    """
    Returns a string that can be used as a filename for the inspection report.
    """
    inspection_item = inspection_obj.get_json().get("item")
    if not inspection_item:
        return "Inspection_report.pdf"
    reg_no = get_reg_no(inspection_obj)
    datetime_str = date_as_str(inspection_obj.created)
    return f"inspection-report-{reg_no}-{datetime_str}.pdf"


def report_context(inspection_id):
    inspection_obj = get_object_or_404(Inspection, pk=inspection_id)
    mixin_obj = InspectionContextMixin(obj=inspection_obj)

    context = {
        "object": inspection_obj,
        "report_name": report_name(inspection_obj),
        "axle_list": mixin_obj.get_axel_list(),
        "pdfnote": mixin_obj.get_pdfnote(),
        "failed_items": mixin_obj.get_failed_items(),
        "monitored_items": mixin_obj.get_monitored_items(),
    }
    return context


def get_pdf_content(inspection_id):
    template = "inspections/inspection_detail_print.html"
    context = report_context(inspection_id)
    html_string = render_to_string(template, context)
    pdf_content = pdfkit.from_string(html_string, False)
    filename = context["report_name"]
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def get_emails(template_id, inspector_obj):
    template_obj = get_object_or_404(InspectionTemplateProfile, pk=template_id)
    static_emails = validate_email_list(template_obj.emails)
    static_emails = validate_email_list(template_obj.emails)

    contractor_id = inspector_obj.profile.contractor.id
    filter_query = Q(profile__contractor_id=contractor_id)
    user_qs = User.objects.filter(filter_query)
    admin_qs = user_qs.filter(groups__name__icontains="admin")
    admin_emails = list(admin_qs.values_list('email'))
    for index, email in enumerate(admin_emails):
        admin_emails[index] = email[0]
    email_list = static_emails + admin_emails
    return list(dict.fromkeys(email_list))


def send_inspection_submitted_email(inspection_id, request):
    """ Sends an email to all admins regarding inspection submission."""

    inspection_obj = get_object_or_404(Inspection, pk=inspection_id)
    inspection_json = inspection_obj.get_json()

    if inspection_json:
        template_id = inspection_json.get("template_id", 1)  # change this
        if template_id:
            inspector_obj = inspection_obj.submitted_by
            context = {
                "inspector_name": inspector_obj.get_full_name(),
                "submission_date": inspection_obj.submitted,
                "inspection_item": inspection_obj.inspection_item,
                "inspection_id": inspection_id,
                'domain': get_domain(request),
                'site_name': get_domain(request),
                'protocol': get_protocol(request),
            }

            template = get_template('inspections/email/inspection_submission.html')
            content = template.render(context)
            email_list = get_emails(template_id, inspector_obj)
            subject = "New Inspection Submission Notification"
            send_mail(subject, content, settings.EMAIL_HOST_USER, email_list)
