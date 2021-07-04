# Generated by Django 3.1.2 on 2020-10-22 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20201022_1551'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=254)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('q', models.CharField(blank=True, max_length=2500)),
                ('g', models.CharField(blank=True, max_length=2500)),
                ('voter_registration_open', models.BooleanField(default=False, null=True)),
                ('tallying_authority_registration_open', models.BooleanField(default=False, null=True)),
                ('voting_enabled', models.BooleanField(default=False, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tallyingauthority',
            name='is_registered',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='voter',
            name='a_reference',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='voter',
            name='b_reference',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='voter',
            name='has_voted',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='voter',
            name='reference',
            field=models.CharField(blank=True, max_length=254),
        ),
    ]