from django.urls import path
from search.views import (
    SearchInspectionListView
)


urlpatterns = [
    path('', SearchInspectionListView.as_view(), name='query')
]
