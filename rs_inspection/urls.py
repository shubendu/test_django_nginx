from django.contrib import admin
from django.urls import include, path
from django.urls import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
# from inspection_template.views import CustomizedInspectionTemplateApiView
from inspections.views import (InspectionViewSet,
                               InspectionItemViewSet,
                               InspectionItemTypeViewSet,
                               InspectionItemSearch,
                               DownloadInspectionReport
                               )
from pages.views import FaciconView
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views
from users.views import ContractorViewSet
from users.views import UserViewSet
from users.views import ContractorTemplates
from users.views import PasswordResetSendEmailAPI
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'inspections', InspectionViewSet, basename='inspection')
router.register(r'items', InspectionItemViewSet, basename='inspectionitem')
router.register(r'item-types', InspectionItemTypeViewSet)
router.register(r'contractors', ContractorViewSet)
router.register(r'contractor-templates',
                ContractorTemplates, basename='templates')
# router.register(r'custom-questions', CustomizedInspectionTemplateApiView)

# Swagger Config
schema_view = get_schema_view(
    openapi.Info(
        title="RS Recovery API",
        default_version='v1',
        description="API docs for RS Recovery",
        terms_of_service="",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
# End Swagger Config


urlpatterns = [
    path('favicon.ico', FaciconView),
    path('admin/inspection_template/templatequestion/add/',
         RedirectView.as_view(
             url=reverse_lazy('create_custom_template'))
         ),
    path('admin/', admin.site.urls),
    # path('api-auth/', include('rest_framework.urls')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/items/search/<str:search>/',
         InspectionItemSearch.as_view(), name='item_search'),
    path('api/inspection-report/<str:id>/',
         DownloadInspectionReport.as_view(), name='inspection_report'),
    path('api/password-reset-email/', PasswordResetSendEmailAPI.as_view(),),
    path('api/', include(router.urls)),
    # path('api/user/', CurrentUserView.as_view(), name='api_current_user'),
    path('inspections/', include('inspections.urls')),
    path('inspection-template/',
         include('inspection_template.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('manage-vehicle/', include('vehicle.urls')),
    path('settings/', include('config_app.urls')),
    path('search/', include(('search.urls', 'search'), namespace='search')),
    path('', include('pages.urls')),
    path('tinymce/', include('tinymce.urls')),  # tinymce in admin
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger',
                                               cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc',
                                             cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

# # path('account/', include('django.contrib.auth.urls')),
# accounts/login/ [name='login']
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/reset/done/ [name='password_reset_complete']
