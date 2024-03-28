import pdfkit

from config_app.models import AdminContent
from config_app.mixins import MyLoginRequiredMixin

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic.list import ListView, MultipleObjectMixin
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin

from inspections.models import Inspection, InspectionItem, InspectionItemType
from inspections.mixins import InspectionContextMixin
from inspections.mixins import CheckInspectionAccessMixin
from inspections.serializers import InspectionItemSerializer
from inspections.serializers import InspectionItemTypeSerializer
from inspections.serializers import InspectionSerializer
from inspections.utils import get_pdf_content, send_inspection_submitted_email

from rest_framework import viewsets
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from users.mixins import UserTypeMixin


@login_required
def inspection_pdf_report(request, *args, **kwargs):
    inspection_id = kwargs.get("pk")
    return get_pdf_content(inspection_id)

# ########### API ##########################


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer

    def get_queryset(self):
        user_type_obj = UserTypeMixin()
        user_type = user_type_obj.get_user_type(self.request.user, self.request)
        qs = super(InspectionViewSet, self).get_queryset(
        ).by_user_type(user_type, self.request)
        return qs.order_by('-submitted')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspection = serializer.save()
        headers = self.get_success_headers(serializer.data)
        send_inspection_submitted_email(inspection_id=inspection.id, request=request)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class InspectionItemViewSet(viewsets.ModelViewSet):
    queryset = InspectionItem.objects.all()
    serializer_class = InspectionItemSerializer


class InspectionItemSearch(generics.ListAPIView):
    serializer_class = InspectionItemSerializer

    def get_queryset(self):
        search = self.kwargs['search']
        return InspectionItem.objects.filter(ref__icontains=search)


class DownloadInspectionReport(generics.RetrieveAPIView):
    serializer_class = InspectionSerializer
    queryset = Inspection.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        inspection_id = self.kwargs['id']
        return get_pdf_content(inspection_id)


class InspectionItemTypeViewSet(viewsets.ModelViewSet):
    queryset = InspectionItemType.objects.all()
    serializer_class = InspectionItemTypeSerializer


# Frontend #######################
@login_required
def index(request):
    inspections = Inspection.objects.all()
    context = {}
    return render(request, 'inspections/index.html', context)
    # return HttpResponse("Home page")


class InspectionList(MyLoginRequiredMixin, PermissionRequiredMixin, ListView, UserTypeMixin):
    model = Inspection
    permission_required = ('inspections.view_inspection',)
    paginate_by = 20
    ordering = ['-created', ]
    login_url = 'contractor_login'

    def get_ordering(self):
        ordering = self.request.GET.get('order')
        if ordering in ['inspection_item', '-inspection_item', 'inspection_item__item_type', 'inspection_item__item_type', 'id', '-id', 'submitted', '-submitted', 'submitted_by', '-submitted_by']:
            return [ordering, ]
        return self.ordering

    def get_queryset(self):
        user_type = self.get_user_type(self.request.user, self.request)
        qs = super(InspectionList, self).get_queryset(
        ).by_user_type(user_type, self.request)
        return qs


class InspectionDetail(MyLoginRequiredMixin, CheckInspectionAccessMixin, InspectionContextMixin, DetailView):
    model = Inspection


class InspectionDetailPrint(MyLoginRequiredMixin, CheckInspectionAccessMixin, InspectionContextMixin, DetailView):
    model = Inspection
    template_name = 'inspections/inspection_detail_print.html'


class InspectionItemList(MyLoginRequiredMixin, ListView):
    model = InspectionItem
    paginate_by = 20
    ordering = ['-created', ]

    def get_ordering(self):
        ordering = self.request.GET.get('order')
        if ordering in ['ref', '-ref', 'created', 'id', '-id', 'item_type', '-item_type', 'created_by', '-created_by']:
            return [ordering, ]
        return self.ordering


class InspectionItemDetail(MyLoginRequiredMixin, DetailView, MultipleObjectMixin):
    model = InspectionItem
    paginate_by = 10
    order_by = '-created'

    def get_context_data(self, **kwargs):
        object_list = Inspection.objects.filter(
            inspection_item=self.get_object()).order_by(self.get_order_by())
        context = super(InspectionItemDetail, self).get_context_data(
            object_list=object_list, **kwargs)
        return context

    def get_order_by(self):
        order_by = self.request.GET.get('order')
        if order_by in ['inspection_item', '-inspection_item', 'inspection_item__item_type', 'inspection_item__item_type', 'id', '-id', 'submitted', '-submitted', 'submitted_by', '-submitted_by']:
            return order_by
        return self.order_by
