from django.urls import path
from config_app.views import (
    SettingsHomeView,
    InspectorListView,
    InspectorDetail,
    TermsAndConditions,
    PrivacyPolicy,
    InpsectorDeleteView,
)


urlpatterns = [
    path('', SettingsHomeView.as_view(), name='settings_home'),
    path('inspectors/', InspectorListView.as_view(), name='inspector_list'),
    path(
        'inspectors/<int:pk>/',
        InspectorDetail.as_view(),
        name='inspector_detail'
    ),
    path(
        'inspectors/<int:pk>/delete/',
        InpsectorDeleteView.as_view(),
        name='inspector_delete'
    ),
    path('terms-and-conditions/', TermsAndConditions.as_view(), name='terms'),
    path('privacy-policy/', PrivacyPolicy.as_view(), name='privacy_policy'),
]
