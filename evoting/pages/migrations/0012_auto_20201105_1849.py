# Generated by Django 3.1.2 on 2020-11-05 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0011_tallyingauthority_result_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='no_count',
            field=models.CharField(blank=True, max_length=2500),
        ),
        migrations.AddField(
            model_name='candidate',
            name='yes_count',
            field=models.CharField(blank=True, max_length=2500),
        ),
    ]