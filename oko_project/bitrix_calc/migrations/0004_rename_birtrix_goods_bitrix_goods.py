# Generated by Django 5.1 on 2024-11-18 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0030_goodscomposition_name_type_of_goods_and_more'),
        ('bitrix_calc', '0003_birtrix_goods_folder'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Birtrix_Goods',
            new_name='Bitrix_Goods',
        ),
    ]
