# Generated by Django 5.1 on 2024-11-13 11:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0027_productcomposition_techoperation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.folder', verbose_name='Папка'),
        ),
    ]
