from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import (InspectionTemplateProfile,
                     Template,
                     Category,
                     Question)


class ArrayField(serializers.ListField):

    def to_representation(self, value):
        """ Convert string to a list of integers"""
        value_list = [val if val != "-" else 0 for val in value.split(',')]
        if value_list == ['']:
            return []
        return super().to_representation(value_list)


class QuestionSerializer(ModelSerializer):
    im_array = ArrayField(child=serializers.IntegerField())

    class Meta:
        model = Question
        fields = ('question', 'im_array',)


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "label", "sort_order", ]


class TemplateQuestionSerializer(ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Template
        fields = ["category", "questions"]


class InspectionTemplateProfileSerializer(ModelSerializer):
    template = TemplateQuestionSerializer(read_only=True)

    class Meta:
        model = InspectionTemplateProfile
        fields = ['template', ]
