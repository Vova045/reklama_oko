# Generated by Django 5.1 on 2024-11-17 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_goods_goodscomposition'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodscomposition',
            name='name_type_of_goods',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Наименование типа товара'),
        ),
        migrations.AddField(
            model_name='goodscomposition',
            name='type_of_goods',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Тип товара'),
        ),
    ]
