from rest_framework import serializers
from django.contrib.auth.models import User
from inspection_template.models import InspectionTemplateProfile
from .models import Contractor, Profile


class ContractorSerializerLimitedFields(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = ['id', 'name', ]


class ContractorTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = ('inspection_template',)


class ContractorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Contractor
        exclude = ['created', 'modified', 'inspection_template']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    # contractor = ContractorSerializer()
    class Meta:
        model = Profile
        fields = ['contractor_name', 'contractor', ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email',
                  'is_staff', 'get_full_name', 'profile', ]
