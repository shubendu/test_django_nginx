# Generated by Django 3.2.16 on 2023-08-18 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inspection_template', '0003_add_validation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspectiontemplateprofile',
            name='vehicle_type',
            field=models.CharField(choices=[('trailer', 'trailer'), ('powered_vehicle', 'powered_vehicle')], max_length=20),
        ),
    ]