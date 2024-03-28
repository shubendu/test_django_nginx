from django.contrib import admin
from .models import Inspection, InspectionItem, InspectionItemType


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'inspection_item', 'created',
                    'created_by', 'submitted', 'submitted_by')
    readonly_fields = (
        'created',
        'created_by',
        'submitted',
        'submitted_by',
    )


@admin.register(InspectionItem)
class InspectionItemAdmin(admin.ModelAdmin):
    readonly_fields = ('created_by', )
    list_display = ('__str__', 'item_type', 'created_by', 'created')

    def get_readonly_fields(self, request, obj=None):
        if (obj):
            return ('item_type',) + self.readonly_fields
        return self.readonly_fields


@admin.register(InspectionItemType)
class InspectionItemTypeAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    pass
