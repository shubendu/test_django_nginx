from config_app.choices import UserTypes
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from users.models import Contractor


User = get_user_model()


class CustomPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        # Check if the user is authenticated
        if not user.is_authenticated:
            return False

        # Check if the user is a superuser
        if user.is_superuser:
            return True

        grant_permissions = user.user_permissions.values_list(
            'codename', flat=True)
        for perm in self.permission_required:
            if perm not in grant_permissions:
                return False
        return True

    def handle_no_permission(self):
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        return super().handle_no_permission()


class UserTypeMixin(object):

    def filter_user_qs(self, user_qs, request):
        user_type = request.session.get('user_type')
        contractor_id = request.session.get('contractor_id')

        if not user_type:
            user_type = self.get_user_type(request.user)

        if "super_admin" in user_type:
            return user_qs

        filter_query = Q(profile__contractor_id=contractor_id)
        if any(x in user_type for x in [UserTypes.contractor_admin, UserTypes.viewer, UserTypes.inspector]):
            if contractor_id is None:
                return None
            return user_qs.filter(filter_query)
        return None

    def get_user_type(self, user, request=None):
        user_type = ""
        if user.is_superuser:
            return UserTypes.super_admin
        
        if user.groups.filter(name__icontains="admin").exists():
            user_type =  f"{user_type}_{UserTypes.contractor_admin}"
        if user.groups.filter(name__icontains="inspector").exists():
            user_type = f"{user_type}_{UserTypes.inspector}"
        if user.groups.filter(name__icontains="view").exists():
            user_type = f"{user_type}_{UserTypes.viewer}"
        return user_type.strip("_")


class UserExistsMixin(object):
    def user_exists(self, email):
        if not email:
            self.response_message = _('Email is required')
            return False, None
        user_qs = User.objects.filter(email=email)
        if not user_qs.exists():
            self.response_message = _('User does not exist')
            return False, None
        return True, user_qs.first()


class SendEmailMixin(object):
    def send_email(self, email, context):
        html_message = render_to_string(
            self.email_template_name, context)
        send_mail(self.subject, html_message, settings.EMAIL_HOST_USER,
                  [email, ], fail_silently=False)
