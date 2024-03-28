from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from config_app.choices import VehicleTypes
from django.db.models.signals import pre_delete
from django.dispatch import receiver


def validate_email_list(email_list):
    updated_list = []
    if email_list:
        email_list = email_list.split(",")
        for email in email_list:
            email = email.strip()
            if not email:
                continue
            try:
                validate_email(email)
                updated_list.append(email)
            except ValidationError:
                raise ValidationError(f"'{email}' is not a valid email address.")
    return updated_list


class Question(models.Model):
    question = models.TextField()
    im_array = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.question


class Category(models.Model):
    category_id = models.CharField(max_length=128)
    label = models.CharField(max_length=128)
    questions = models.ManyToManyField(Question)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.label


class Template(models.Model):
    name = models.CharField(max_length=128)
    category = models.ManyToManyField(Category)
    include_tyre_break_section = models.BooleanField(default=True, blank=True, null=True)

    def __str__(self):
        return self.name


@receiver(pre_delete, sender=Template)
def delete_cats(sender, instance, **kwargs):
    # delete categories prior to deleting template
    instance.category.all().delete()

@receiver(pre_delete, sender=Category)
def delete_questions(sender, instance, **kwargs):
    # delete questions prior to deleting category
    instance.questions.all().delete()


class InspectionTemplateProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    name = models.CharField(max_length=128)
    vehicle_type = models.CharField(max_length=20, choices=VehicleTypes)
    template = models.ForeignKey(
        Template, null=True, on_delete=models.SET_NULL, blank=True)
    emails = models.TextField(
        blank=True,
        null=True,
        help_text=(
            "Email addresses separated by commas."
            "\nLink to download inspection report will be sent after inspection."
        ),
        validators=[validate_email_list],
    )

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.name
