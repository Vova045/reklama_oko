# Generated by Django 3.2.25 on 2024-11-24 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0033_bitrixuser_refresh_token_ttl_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitrixuser',
            name='bitrix_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]