from vehicle.views import upload_vehicle_page
from django.urls import path

urlpatterns = [
    path("", upload_vehicle_page, name="upload_vehicle_page"),
]
