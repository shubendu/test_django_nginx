import hashlib
import urllib
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save  # noqa
from django.dispatch import receiver  # noqa
from inspection_template.models import InspectionTemplateProfile
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
# User = get_user_model()


class Contractor(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=64)
    address1 = models.CharField(blank=True, null=True, max_length=64)
    address2 = models.CharField(blank=True, null=True, max_length=64)
    town = models.CharField(blank=True, null=True, max_length=64)
    county = models.CharField(blank=True, null=True, max_length=64)
    postcode = models.CharField(blank=True, null=True, max_length=8)
    logo = models.ImageField(blank=True, null=True,
                             upload_to='media/images/contractor_logos')
    inspection_template = models.ManyToManyField(
        InspectionTemplateProfile, blank=True)

    def __str__(self):
        return '{}'.format(self.name)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contractor_name = models.CharField(blank=True, max_length=64)
    contractor = models.ForeignKey(
        Contractor, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{}'.format(self.user.username)

    def get_avatar_url(self):
        default = "mp"
        size = 40
        return "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(self.user.email.lower().encode()).hexdigest(), urllib.parse.urlencode({'d': default, 's': str(size)}))
