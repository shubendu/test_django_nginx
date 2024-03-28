from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import AccessMixin
from users.mixins import UserTypeMixin
from django.http import HttpResponseForbidden


class CustomPermissionRequiredMixin(AccessMixin):
    allowed_users = []

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            return HttpResponseForbidden("You don't have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self, request):
        user = request.user
        user_type_obj = UserTypeMixin()
        user_type = user_type_obj.get_user_type(user, request)
        if any(user in user_type.lower() for user in self.allowed_users) or user.is_superuser:
            return True
        else:
            return False  # Deny access if no custom permission is specified


class MyLoginRequiredMixin(LoginRequiredMixin):
    login_url = 'contractor_login'
