from config_app.models import AdminContent
from inspections.models import Inspection
from config_app.mixins import MyLoginRequiredMixin

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from config_app.mixins import CustomPermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse_lazy


class SettingsHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'config_app/settings_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Settings'
        return context


class InspectorListView(
    LoginRequiredMixin,
    CustomPermissionRequiredMixin,
    TemplateView
):
    template_name = 'config_app/inspector_list.html'
    allowed_users = ['contractor_admin', 'viewer']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Inspectors'
        context['inspectors'] = self.get_queryset()
        return context

    def get_queryset(self):
        user = self.request.user
        order_by = self.request.GET.get('order', None)

        if user.is_superuser:
            qs = User.objects.filter(groups__name='Inspector')
        else:
            # contractor = Contractor.objects.filter(user=user).first()
            # try:
            contractor = user.profile.contractor
            # except:
            #     contractor = None
            qs = User.objects.filter(
                groups__name='Inspector', profile__contractor=contractor)
        if order_by is not None:
            qs = qs.order_by(order_by)
        return qs


class InspectorDetail(MyLoginRequiredMixin, CustomPermissionRequiredMixin, DetailView, MultipleObjectMixin):
    allowed_users = ['contractor_admin', 'viewer']
    model = User
    paginate_by = 10
    order_by = '-created'
    template_name = 'config_app/inspector_detail.html'

    def get_context_data(self, **kwargs):
        object_list = Inspection.objects.filter(
            submitted_by=self.get_object()).order_by(self.get_order_by())
        context = super(InspectorDetail, self).get_context_data(
            object_list=object_list, **kwargs)
        return context

    def get_order_by(self):
        order_by = self.request.GET.get('order')
        if order_by in ['inspection_item', '-inspection_item', 'inspection_item__item_type', 'inspection_item__item_type', 'id', '-id', 'submitted', '-submitted', 'submitted_by', '-submitted_by']:
            return order_by
        return self.order_by


class InpsectorDeleteView(DeleteView):
    model = User
    template_name = 'config_app/delete_view.html'
    success_url = reverse_lazy("inspector_list")
    success_message = "Inspector deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(request, self.success_message)
        return super(InpsectorDeleteView, self).delete(request, *args, **kwargs)


class TermsAndConditions(TemplateView):
    template_name = 'config_app/privacy_terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms = AdminContent.objects.filter(title='terms&conditions').first()
        if terms:
            context['object'] = terms
        else:
            context['message'] = 'No terms and conditions yet added.'
        return context


class PrivacyPolicy(TemplateView):
    template_name = 'config_app/privacy_terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        privacy = AdminContent.objects.filter(title='privacypolicy').first()
        if privacy:
            context['object'] = privacy
        else:
            context['message'] = 'No privacy policy yet added.'
        return context
