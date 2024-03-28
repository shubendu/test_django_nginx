# Generated by Django 3.1.2 on 2020-11-07 17:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0008_inspectionitemtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspectionitem',
            name='item_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='inspections.inspectionitemtype'),
            preserve_default=False,
        ),
    ]
