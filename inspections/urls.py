from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path("generate-pdf/<int:pk>/", views.inspection_pdf_report, name="generate_pdf"),
    path('', views.InspectionList.as_view(), name='inspections-list'),
    path('<int:pk>/', views.InspectionDetail.as_view(), name='inspections-detail'),
    path('<int:pk>/print', views.InspectionDetailPrint.as_view(), name='inspections-detail-print'),
    path('profiles/', views.InspectionItemList.as_view(), name='inspection-items-list'),
    path('profiles/<int:pk>/', views.InspectionItemDetail.as_view(), name='inspection-items-detail'),
]
