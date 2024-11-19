# Generated by Django 5.1.3 on 2024-11-19 07:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_bitrixuser_expires_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitrixuser',
            name='refresh_token_created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
