from rest_framework import serializers
from .models import Inspection, InspectionItem, InspectionItemType


class InspectionSerializer(serializers.HyperlinkedModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    inspection_json = serializers.JSONField()
    inspector_name = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Inspection
        fields = [
            'url',
            'id',
            'created_by',
            'inspector_name',
            'created',
            'modified',
            'submitted_by',
            'submitted',
            'inspection_json',
            'inspection_item'
        ]

    def get_inspector_name(self, obj):
        if obj.submitted_by:
            return obj.submitted_by.get_full_name()
        elif obj.created_by:
            return obj.created_by.get_full_name()
        return None


class InspectionItemSerializer(serializers.HyperlinkedModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    item_json = serializers.JSONField()

    class Meta:
        model = InspectionItem
        fields = [
            'id',
            'url',
            'ref',
            'item_json',
            'item_type',
            'created_by'
        ]


class InspectionItemTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InspectionItemType
        fields = [
            'url',
            'name'
        ]
