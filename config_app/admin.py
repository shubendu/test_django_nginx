from django.contrib import admin
from config_app.models import AdminContent
from django.db import models
from tinymce.widgets import TinyMCE

admin.site.site_header = 'Rs Recovery Administration'
admin.site.site_title = 'Rs Recovery Admin'
admin.site.index_title = 'Rs Recovery Admin'


class StaticContent(admin.ModelAdmin):
    verbose_name_plural = 'Static Content'
    list_display = ["title", "last_updated", "created"]
    readonly_fields = ["title"]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return True


admin.site.register(AdminContent, StaticContent)
