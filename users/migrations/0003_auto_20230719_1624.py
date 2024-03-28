# Generated by Django 3.2.16 on 2023-07-19 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspection_template', '__first__'),
        ('users', '0002_auto_20201223_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractor',
            name='inspection_template',
            field=models.ManyToManyField(blank=True, to='inspection_template.InspectionTemplateProfile'),
        ),
        migrations.AddField(
            model_name='contractor',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='media/images/contractor_logos'),
        ),
    ]
