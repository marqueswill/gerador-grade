# Generated by Django 3.0.8 on 2020-08-06 04:52

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0016_auto_20200806_0449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='flow',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='flow_graph',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='num_semester',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]