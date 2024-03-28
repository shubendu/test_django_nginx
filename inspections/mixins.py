from config_app.models import AdminContent
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import AccessMixin
from users.mixins import UserTypeMixin
from django.http import HttpResponseForbidden


class CheckInspectionAccessMixin(AccessMixin):
    allowed_users = []

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request):
            return HttpResponseForbidden("You don't have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self, request):
        user = request.user
        if user.is_superuser:
            return True
        submitted_by = self.get_object().submitted_by
        try:
            if submitted_by.profile.contractor != user.profile.contractor:
                return False
        except Exception as e:
            return False

        user_type_obj = UserTypeMixin()
        user_type = user_type_obj.get_user_type(user, request)
        if (user == submitted_by or
            "admin" in user_type.lower() or "viewer" in user_type.lower()):
            return True
        else:
            return False

class InspectionContextMixin(object):

    def __init__(self, obj=None):
        self._inspection_obj = obj

    def get_inspection_obj(self):
        if self._inspection_obj:
            return self._inspection_obj
        return super().get_object()

    def get_pdfnote(self):
        pdfnote = AdminContent.objects.filter(title='pdfnote').first()
        if pdfnote:
            return pdfnote.content
        return None

    def get_axel_list(self):
        inspection_obj = self.get_inspection_obj()
        if inspection_obj.get_json().get("item"):
            return inspection_obj.get_json()["item"].get("axles", None)
        return None

    def get_failed_items(self):
        rectificationsFail = []
        inspection_obj = self.get_inspection_obj()
        categories = inspection_obj.get_json().get('questions')

        for id in inspection_obj.category_ids:
            if id not in categories:
                continue
            category = categories[id]
            for question in category['questions']:
                if 'value' in question and question['value'] == 'failed':
                    rectificationsFail.append(question)
        return rectificationsFail

    def get_monitored_items(self):
        rectificationsMonitor = []
        inspection_obj = self.get_inspection_obj()
        categories = inspection_obj.get_json().get('questions')

        for id in inspection_obj.category_ids:
            if id not in categories:
                continue
            category = categories[id]
            for question in category['questions']:
                if 'value' in question and question['value'] == 'monitor':
                    rectificationsMonitor.append(question)
        return rectificationsMonitor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['axle_list'] = self.get_axel_list()
        context['pdfnote'] = self.get_pdfnote()
        context['failed_items'] = self.get_failed_items()
        context['monitored_items'] = self.get_monitored_items()
        return context
