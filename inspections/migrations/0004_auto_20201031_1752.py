# Generated by Django 3.1.2 on 2020-10-31 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0003_auto_20201031_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspection',
            name='inspection_json',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
