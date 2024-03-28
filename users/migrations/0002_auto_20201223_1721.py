# Generated by Django 3.1.2 on 2020-12-23 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contractor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=64)),
                ('address1', models.CharField(blank=True, max_length=64, null=True)),
                ('address2', models.CharField(blank=True, max_length=64, null=True)),
                ('town', models.CharField(blank=True, max_length=64, null=True)),
                ('county', models.CharField(blank=True, max_length=64, null=True)),
                ('postcode', models.CharField(blank=True, max_length=8, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='contractor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.contractor'),
        ),
    ]