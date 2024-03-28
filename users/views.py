from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.generic.list import ListView
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.forms.models import inlineformset_factory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from config_app.mixins import MyLoginRequiredMixin
from config_app.mixins import CustomPermissionRequiredMixin
from config_app.choices import UserTypes
from inspection_template.models import InspectionTemplateProfile
from inspection_template.utils import fetch_questions
from inspections.models import Inspection

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from config_app.utils import get_domain, get_protocol

from users.forms import UserEditForm
from users.forms import UserAddForm
from users.forms import PasswordForm
from users.forms import Login_form
from users.models import Profile
from users.models import Contractor
from users.serializers import ContractorSerializer
from users.serializers import ContractorSerializerLimitedFields
from users.serializers import UserSerializer
from users.serializers import ContractorTemplateSerializer
from users.utils import check_contractor_login
from users.utils import check_user_is_contractor
from users.mixins import (
    UserExistsMixin,
    # CustomPermissionMixin,
    SendEmailMixin,
    UserTypeMixin,)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated, ])
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        is_contractor, obj = check_user_is_contractor(user=request.user, request=request)
        data = serializer.data
        if is_contractor:
            http = "http://" if not request.is_secure() else "https://"
            profile = {
                "contractor_name": obj.name,
                "contractor": f"{http}{request.META['HTTP_HOST']}/api/contractors/{obj.id}/",
            }
            data['profile'] = profile
        return Response(data)


class ContractorTemplates(viewsets.ModelViewSet, UserTypeMixin):
    queryset = Contractor.objects.all()
    serializer_class = ContractorTemplateSerializer

    def list(self, request):
        inspector_user = request.user
        user_type = self.get_user_type(inspector_user, request)

        user_allowed = any(x in user_type.lower() for x in [UserTypes.contractor_admin, UserTypes.inspector])
        if not user_allowed:
            response = {"message": "You are not allowed to perform this action"}
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        vehicle_type = request.GET.get('vehicle_type')
        contractor = inspector_user.profile.contractor
        serializer = self.get_serializer(contractor)
        response = serializer.data

        inspection_templates = InspectionTemplateProfile.objects.filter(
            id__in=response['inspection_template']
        ).only("id", "name", "vehicle_type")

        if vehicle_type:
            inspection_templates = inspection_templates.filter(vehicle_type=vehicle_type)

        inspection_template = [
            {
                "template_id": template.id,
                "name": template.name,
                "vehicle_type": template.vehicle_type,
                "include_tyre_break_section": template.template.include_tyre_break_section,
                "category_set": fetch_questions(template),
                
            }
            for template in inspection_templates
        ]

        response['inspection_template'] = inspection_template
        return Response(response, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = serializer.data
        inspection_templates = response['inspection_template']
        inspection_template = []
        for template_id in inspection_templates:
            obj = InspectionTemplateProfile.objects.get(id=template_id)
            data = {
                "id": template_id,
                "name": obj.name,
            }
            inspection_template.append(data)
        response['inspection_template'] = inspection_template
        return Response(response)


class ContractorViewSet(viewsets.ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer

    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated, ], url_path='contractors-list')
    def contractors_list(self, request):
        contractors = Contractor.objects.all()
        serializer = ContractorSerializerLimitedFields(contractors, many=True)
        return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes((permissions.AllowAny,))
# def current_user(request):
#     serializer = UserSerializer(request.user)
#     return Response(serializer.data) # data return the serialised object {}

# @permission_classes((permissions.AllowAny,)) # Override default permission class (ModelPermissions) as we don't use a model here
# class CurrentUserView(APIView):
#     def get(self, request):
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)


class UserList(
    MyLoginRequiredMixin,
    CustomPermissionRequiredMixin,
    ListView,
    UserTypeMixin
):
    allowed_users = ['contractor_admin',]
    model = User
    paginate_by = 20
    ordering = ['username', ]
    login_url = 'contractor_login'

    def get_ordering(self):
        ordering = self.request.GET.get('order')
        if ordering in [
            'id', '-id',
            'username', '-username',
            'first_name', '-first_name',
            'last_name', '-last_name',
            'profile__contractor__name', '-profile__contractor__name',
            'is_active', '-is_active',
        ]:
            return [ordering, ]
        return self.ordering

    def get_queryset(self):
        queryset = super(UserList, self).get_queryset()
        return self.filter_user_qs(queryset, self.request)

# class UserDetail(MyLoginRequiredMixin, DetailView):
#     model = User


class UserDetail(MyLoginRequiredMixin, CustomPermissionRequiredMixin, DetailView, MultipleObjectMixin):
    allowed_users = ['contractor_admin', 'viewer']
    model = User
    paginate_by = 10
    order_by = '-created'

    def get_context_data(self, **kwargs):
        object_list = Inspection.objects.filter(
            submitted_by=self.get_object()).order_by(self.get_order_by())
        context = super(UserDetail, self).get_context_data(
            object_list=object_list, **kwargs)
        user_object = self.get_object()
        user_permissions = user_object.user_permissions.values_list(
            'codename', flat=True)
        context['user_permissions'] = user_permissions
        return context

    def get_order_by(self):
        order_by = self.request.GET.get('order')
        if order_by in ['inspection_item', '-inspection_item', 'inspection_item__item_type', 'inspection_item__item_type', 'id', '-id', 'submitted', '-submitted', 'submitted_by', '-submitted_by']:
            return order_by
        return self.order_by


UserProfileFormset = inlineformset_factory(
    User, Profile, fields=('contractor',), can_delete=False
)


class UserEdit(MyLoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    allowed_users = ('contractor_admin',)
    form_class = UserEditForm
    model = User

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["profile"] = UserProfileFormset(
                self.request.POST, instance=self.object)
        else:
            data["profile"] = UserProfileFormset(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        profile = context["profile"]
        self.object = form.save()
        if profile.is_valid():
            profile.instance = self.object
            profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("user-detail", kwargs={'pk': self.object.pk})


class UserAdd(MyLoginRequiredMixin, CustomPermissionRequiredMixin, UserTypeMixin, CreateView):
    allowed_users = ('contractor_admin',)
    model = User
    form_class = UserAddForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        request = self.request
        user_type = self.get_user_type(request.user, request)
        request.session['user_type'] = user_type
        if not 'contractor_admin' in user_type.lower():
            if request.POST:
                data["profile"] = UserProfileFormset(request.POST)
            else:
                data["profile"] = UserProfileFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        request = self.request
        self.object = form.save()

        if request.user.is_superuser:
            profile = context["profile"]
            if profile.is_valid():
                profile.instance = self.object
                profile.save()
        else:
            contractor = Contractor.objects.get(id=request.session['contractor_id'])
            profile = Profile(user=self.object, contractor=contractor, contractor_name=contractor.name)
            profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("user-detail", kwargs={'pk': self.object.pk})


class UserChangePassword(MyLoginRequiredMixin, CustomPermissionRequiredMixin, UpdateView):
    allowed_users = ('contractor_admin',)
    form_class = PasswordForm
    model = User


class ContractorLoginView(FormView):
    form_class = Login_form
    template_name = 'registration/contractor_login.html'

    def get_success_url(self):
        return self.request.GET.get('next', '/')

    def form_invalid(self, form):
        return super(ContractorLoginView, self).form_invalid(form)

    def form_valid(self, form):
        request = self.request
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if check_contractor_login(request, user):
            return super(ContractorLoginView, self).form_valid(form)
        return super(ContractorLoginView, self).form_invalid(form)


class PasswordResetSendEmailAPI(APIView, UserExistsMixin, SendEmailMixin):
    permission_classes = (permissions.AllowAny,)
    email_template_name = 'registration/password_reset_email.html'
    subject = _('Password Reset Requested')
    response_message = _(
        'We have sent you an email with a link to reset your password.')

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        uses_exists, user = self.user_exists(email)
        if uses_exists:
            context = {
                'domain': get_domain(request),
                'site_name': get_domain(request),
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': get_protocol(request),
            }
            self.send_email(user.email, context)
            response = {'success': self.response_message}
            return Response(response, status=status.HTTP_200_OK)
        response = {'error': self.response_message}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
