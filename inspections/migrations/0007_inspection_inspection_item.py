# Generated by Django 3.1.2 on 2020-11-07 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inspections', '0006_auto_20201031_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspection',
            name='inspection_item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='inspections.inspectionitem'),
            preserve_default=False,
        ),
    ]