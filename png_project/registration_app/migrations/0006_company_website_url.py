# Generated by Django 5.1.3 on 2024-12-16 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_app', '0005_company_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='website_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
