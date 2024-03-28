from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from inspections.models import Inspection
from search.utils import filter_by_query, filter_by_formdata
from users.mixins import UserTypeMixin


class SearchInspectionListView(LoginRequiredMixin, ListView, UserTypeMixin):

    template_name = 'search/view.html'
    paginate_by = 20
    model = Inspection

    def get_queryset(self, *args, **kwargs):
        request = self.request
        query = request.GET.get('q', None)
        order_by = request.GET.get('order', None)

        form_data = request.GET
        user_type = self.get_user_type(self.request.user, self.request)

        queryset = super().get_queryset()
        queryset = queryset.by_user_type(user_type, request)

        # process form data
        if form_data.get('vehicleType') or form_data.get('startDate'):
            return filter_by_formdata(form_data, queryset)

        # process query
        if query is not None:
            return filter_by_query(query, queryset)
        # process order by
        if order_by is not None:
            return queryset.order_by(order_by)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        form_data = self.request.GET
        context['vehicle_type'] = form_data.get('vehicleType', None)
        context['start_date'] = form_data.get('startDate', None)
        context['end_date'] = form_data.get('endDate', None)
        context['query'] = self.request.GET.get('q', None)
        return context
