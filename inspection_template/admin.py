from django.contrib import admin
from inspection_template.models import (
    InspectionTemplateProfile
)


@admin.register(InspectionTemplateProfile)
class InspectionTemplateProfile(admin.ModelAdmin):
    list_display = ('__str__',)
    add_form_template = "admin/add_inspection_template.html"
    change_form_template = "admin/change_inspection_template.html"
