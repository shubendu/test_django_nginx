# Generated by Django 3.2.16 on 2023-08-07 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspection_template', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspectiontemplateprofile',
            name='emails',
            field=models.TextField(blank=True, help_text='Email addresses separated by commas.\nLink to download inspection report will be sent after inspection.', null=True),
        ),
    ]
