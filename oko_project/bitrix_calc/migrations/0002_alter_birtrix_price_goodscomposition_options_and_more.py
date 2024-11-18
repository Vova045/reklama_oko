# Generated by Django 5.1 on 2024-11-18 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bitrix_calc', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='birtrix_price_goodscomposition',
            options={'verbose_name': 'Цена товара для Битрикса', 'verbose_name_plural': 'Цены товара для Битрикса'},
        ),
        migrations.AlterModelOptions(
            name='bitrix_goodscomposition',
            options={'verbose_name': 'Состав товара для битрикса', 'verbose_name_plural': 'Составы товаров для битрикса'},
        ),
        migrations.AlterModelOptions(
            name='bitrix_goodsparameters',
            options={'verbose_name': 'Параметр товара для битрикса', 'verbose_name_plural': 'Параметры товара для битрикса'},
        ),
        migrations.AlterModelOptions(
            name='bitrix_goodsparametersincalculation',
            options={'verbose_name': 'Параметр товара для Битрикса в калькуляции', 'verbose_name_plural': 'Параметры товара для Битрикса в калькуляции'},
        ),
        migrations.AlterModelOptions(
            name='bitrix_parametersnormatives',
            options={'verbose_name': 'Параметр и Норма для товара для Битрикса', 'verbose_name_plural': 'Параметры и нормы для товара для Битрикса'},
        ),
        migrations.AddField(
            model_name='bitrix_parametersnormatives',
            name='payroll',
            field=models.CharField(blank=True, default=40, max_length=100, null=True, verbose_name='Отчисления на зарплату'),
        ),
        migrations.AlterField(
            model_name='bitrix_parametersnormatives',
            name='overheads',
            field=models.CharField(blank=True, default=100, max_length=100, null=True, verbose_name='Накладные расходы'),
        ),
        migrations.AlterField(
            model_name='bitrix_parametersnormatives',
            name='profit',
            field=models.CharField(blank=True, default=37, max_length=100, null=True, verbose_name='Прибыль'),
        ),
        migrations.AlterField(
            model_name='bitrix_parametersnormatives',
            name='salary_fund',
            field=models.CharField(blank=True, default=69, max_length=100, null=True, verbose_name='Фонд зарплаты'),
        ),
    ]
