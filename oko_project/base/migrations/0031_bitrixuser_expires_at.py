# Generated by Django 5.1.3 on 2024-11-19 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0030_goodscomposition_name_type_of_goods_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitrixuser',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]