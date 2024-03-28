import pytz
from datetime import datetime
from datetime import timedelta
from django.conf import settings
from django.db.models.functions import Concat
from django.db.models import Q, Value


def convert_to_aware_datetime(naive_datetime):
    """
    Convert a naive datetime to a timezone-aware datetime based on the Django project's timezone settings.

    :param naive_datetime: The datetime object or string to convert.
    :type naive_datetime: datetime or str
    :return: The timezone-aware datetime object.
    :rtype: datetime
    :raises ValueError: If the provided `naive_datetime` cannot be parsed or converted to a datetime object.

    Usage:
        # Convert a naive datetime to a timezone-aware datetime
        aware_dt = convert_to_aware_datetime(naive_dt)
    """
    if isinstance(naive_datetime, str):
        naive_datetime = datetime.fromisoformat(naive_datetime)

    time_zone = settings.TIME_ZONE
    tz = pytz.timezone(time_zone)
    aware_datetime = tz.localize(naive_datetime)
    return aware_datetime


def filter_by_formdata(form_data, qs):
    """
    Filter a queryset based on the provided form data.

    :param form_data: The form data containing the filter criteria.
    :type form_data: dict
    :param qs: The queryset to filter.
    :type qs: QuerySet
    :return: The filtered queryset.
    :rtype: QuerySet

    Usage:
        # Example form data
        form_data = {
            'vehicleType': 'car',
            'startDate': '2023-01-01',
            'endDate': '2023-06-30'
        }
        # Filter the queryset based on form data
        filtered_qs = filter_by_formdata(form_data, queryset)
    """
    vehicle_type = form_data.get('vehicleType')
    if vehicle_type:
        qs = qs.filter(
            inspection_item__item_type__name__icontains=vehicle_type)

    start_date = form_data.get('startDate')
    end_date = form_data.get('endDate')

    if start_date:
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        start_datetime = convert_to_aware_datetime(start_date)
        end_datetime = convert_to_aware_datetime(end_date)
        end_datetime = end_datetime + timedelta(days=1)
        qs = qs.filter(submitted__range=[start_datetime, end_datetime])

    return qs


def filter_by_query(query, qs):
    """
    Filter a queryset based on the provided query string.

    :param query: The query string to filter by.
    :type query: str
    :param qs: The queryset to filter.
    :type qs: QuerySet
    :return: The filtered queryset.
    :rtype: QuerySet

    Usage:
        # Example query string
        query = "John Doe"
        # Filter the queryset based on the query string
        filtered_qs = filter_by_query(query, queryset)
    """
    qs = qs.annotate(fullname=Concat('created_by__first_name',
                     Value(' '), 'created_by__last_name'))
    lookups = (
        Q(created__icontains=query) |
        Q(job_number__icontains=query) |
        Q(created_by__username__icontains=query) |
        Q(fullname__icontains=query) |
        Q(submitted_by__username__icontains=query) |
        Q(id__icontains=query) |
        Q(inspection_item__ref__icontains=query)
    )
    return qs.filter(lookups).distinct()
