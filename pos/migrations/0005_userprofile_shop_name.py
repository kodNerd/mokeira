# Generated by Django 5.2.4 on 2025-07-11 15:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0004_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='shop_name',
            field=models.CharField(default=datetime.datetime(2025, 7, 11, 15, 51, 9, 705221, tzinfo=datetime.timezone.utc), max_length=150),
            preserve_default=False,
        ),
    ]
