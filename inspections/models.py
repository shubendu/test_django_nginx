import json
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from config_app.choices import UserTypes


class InspectionItemType(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class InspectionItem(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="item_creator", editable=False)
    modified = models.DateTimeField(auto_now=True)
    ref = models.CharField(max_length=64, unique=True)
    item_json = models.JSONField(blank=True, null=True)
    item_type = models.ForeignKey(InspectionItemType, on_delete=models.PROTECT)

    class Meta:
        ordering = ['created', 'modified']

    def __str__(self):
        return self.ref

    def get_json(self):
        if isinstance(self.item_json, str):
            return json.loads(self.item_json)
        else:
            return self.item_json


class InspectionQuerySet(models.query.QuerySet):

    def by_user_type(self, user_type, request):
        if "super_admin" in user_type:
            return self.filter()
        if "admin" in user_type.lower() or "viewer" in user_type.lower():
            contractor_id = request.session.get('contractor_id')
            if not contractor_id:
                contractor_id = request.user.profile.contractor.id
            return self.filter(submitted_by__profile__contractor__id=contractor_id)
        elif "inspector" in user_type.lower():
            return self.filter(submitted_by=request.user)
        return self.none()

    def search(self, query):
        lookups = (Q(created__icontains=query) |
                   Q(created_by__username__icontains=query) |
                   Q(created_by__first_name__icontains=query) |
                   Q(created_by__last_name__icontains=query) |
                   Q(submitted_by__username__icontains=query) |
                   Q(id__icontains=query) |
                   Q(inspection_item__ref__icontains=query)
                   )
        return self.filter(lookups).distinct()


class InspectionManager(models.Manager):
    def get_queryset(self):
        return InspectionQuerySet(self.model, using=self._db)

    def by_user_type(self, user_type, request):
        return self.get_queryset().by_user_type(user_type, request)

    def search(self, query):
        return self.get_queryset().search(query)


class Inspection(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="inspections_created", editable=False)
    modified = models.DateTimeField(auto_now=True)
    submitted = models.DateTimeField(null=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="inspections_submitted", null=True)
    inspection_json = models.JSONField(blank=True, null=True)
    job_number = models.IntegerField(null=True, blank=True)
    inspection_item = models.ForeignKey(
        InspectionItem, on_delete=models.PROTECT, )

    objects = InspectionManager()
    # status =
    # inspection item
    # inspection form / json

    class Meta:
        ordering = ['created', '-modified']

    def __str__(self):
        return '{} #{}'.format(self.inspection_item, self.pk)

    def get_json(self):
        if isinstance(self.inspection_json, str):
            return json.loads(self.inspection_json)
        else:
            return self.inspection_json

    @property
    def get_inspection_category(self):
        inspection_json = self.get_json()
        if inspection_json and isinstance(inspection_json, dict):
            cats = inspection_json.get('questions', [])
            cats.pop('brakePerformance', None)
            categories = " ".join(cats)
            return categories
        return ""

    @property
    def category_ids(self):
        categories = self.get_inspection_category
        if categories:
            return [cat.strip() for cat in categories.split()]

    @property
    def is_tyre_section_present(self):
        inspection_json = self.get_json()
        if inspection_json and isinstance(inspection_json, dict):
            cats = inspection_json.get('questions', [])
            if 'tyres' in cats:
                return True
        return False


@receiver(post_save, sender=Inspection)
def inspection_post_save(sender, instance, created, **kwargs):
    if created:
        inspection_json = instance.get_json()
        if inspection_json:
            job_no = inspection_json.get("item", {}).get("job_no")
            if job_no:
                instance.job_number = job_no
                instance.save()
