# Generated by Django 3.2.7 on 2021-12-17 01:03

from django.db import migrations, models
import myResidence.models


class Migration(migrations.Migration):

    dependencies = [
        ('myResidence', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TenantLease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lease_address', models.CharField(max_length=255)),
                ('tenant_address', models.CharField(max_length=255)),
                ('tenant_signature', models.ImageField(blank=True, null=True, upload_to=myResidence.models.sign_upload)),
                ('ctc_number', models.IntegerField()),
                ('date_signed', models.DateField()),
            ],
            options={
                'db_table': 'tenant_lease',
                'managed': False,
            },
        ),
    ]
