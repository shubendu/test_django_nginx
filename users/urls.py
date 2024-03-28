from django.urls import path
from users import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.UserList.as_view(), name='users-list'),
    path('add/', views.UserAdd.as_view(), name='user-add'),
    path('<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    path('<int:pk>/edit/', views.UserEdit.as_view(), name='user-edit'),
    path('<int:pk>/password/', views.UserChangePassword.as_view(), name='user-password'),
    path('contractor-login/', views.ContractorLoginView.as_view(), name='contractor_login'),
    # path('profiles/', views.InspectionItemList.as_view(), name='inspection-items-list'),
    # path('profiles/<int:pk>/', views.InspectionItemDetail.as_view(), name='inspection-items-detail'),
]