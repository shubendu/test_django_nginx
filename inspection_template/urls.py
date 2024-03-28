from django.urls import path
from inspection_template.views import (
    custom_category_template,
    custom_question_template,
    create_custom_template,
    EditTemplateView,
    choose_vehicle_type,
    DeleteTemplateView,
    DeleteObjectView
)

urlpatterns = [
    path('choose_vehicle_type/', choose_vehicle_type, name='choose_vehicle_type'),
    path(
        'create_custom_template/',
        create_custom_template,
        name='create_custom_template'
    ),
    path('edit_template/<int:template_id>/',
         EditTemplateView.as_view(), name='edit_template'),
    path(
        'fetch-custom-category/',
        custom_category_template
    ),
    path(
        'fetch-custom-question/',
        custom_question_template
    ),
    path(
        'delete_template/<int:template_id>/',
        DeleteTemplateView.as_view(), name='delete_template'
    ),
    path(
        'delete-object/',
        DeleteObjectView.as_view()
    ),
]
