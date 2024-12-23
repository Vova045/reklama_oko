# Generated by Django 5.0.3 on 2024-10-17 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='addingmaterialstechnologicaloperation',
            options={'verbose_name': 'Добавочный материал Технологической операции', 'verbose_name_plural': 'Добавочные материалы Технологической операции'},
        ),
        migrations.AlterModelOptions(
            name='chaptercalculation',
            options={'verbose_name': 'Раздел калькуляции', 'verbose_name_plural': 'Разделы калькуляции'},
        ),
        migrations.AlterModelOptions(
            name='joptitles',
            options={'verbose_name': 'Должность', 'verbose_name_plural': 'Должности'},
        ),
        migrations.AlterModelOptions(
            name='measureunit',
            options={'verbose_name': 'Единица измерения', 'verbose_name_plural': 'Единицы измерения'},
        ),
        migrations.AlterModelOptions(
            name='operationoftechnologicaloperation',
            options={'verbose_name': 'Операция внутри Технологической операции', 'verbose_name_plural': 'Операции внутри Технологической операции'},
        ),
        migrations.AlterModelOptions(
            name='parametersnormatives',
            options={'verbose_name': 'Параметр и Норма', 'verbose_name_plural': 'Параметры и нормы'},
        ),
        migrations.AlterModelOptions(
            name='productionoperation',
            options={'verbose_name': 'Операция производства', 'verbose_name_plural': 'Операции производства'},
        ),
        migrations.AlterModelOptions(
            name='productionoperationtariffs',
            options={'verbose_name': 'Тариф операции производства', 'verbose_name_plural': 'Тарифы операции производства'},
        ),
        migrations.AlterModelOptions(
            name='technologicallink',
            options={'verbose_name': 'Технический узел', 'verbose_name_plural': 'Технические узлы'},
        ),
        migrations.AlterModelOptions(
            name='technologicallinkcomposition',
            options={'ordering': ('order',), 'verbose_name': 'Состав технологического узла', 'verbose_name_plural': 'Составы технологического узла'},
        ),
        migrations.AddField(
            model_name='materialstechnologicaloperation',
            name='formula',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Формула'),
        ),
        migrations.AddField(
            model_name='technologicaloperation',
            name='formula',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Формула расчета'),
        ),
        migrations.AlterField(
            model_name='chaptercalculation',
            name='chapter_code',
            field=models.CharField(editable=False, max_length=100, unique=True, verbose_name='Код Раздела калькуляции'),
        ),
        migrations.AlterField(
            model_name='nomenklatura',
            name='nomenklatura_code',
            field=models.CharField(editable=False, max_length=100, unique=True, verbose_name='Код коменклатуры'),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_code',
            field=models.CharField(editable=False, max_length=100, unique=True, verbose_name='Код изделия'),
        ),
        migrations.AlterField(
            model_name='productionoperation',
            name='operation_code',
            field=models.CharField(editable=False, max_length=100, unique=True, verbose_name='Код операции производства'),
        ),
        migrations.AlterField(
            model_name='technologicallink',
            name='operation_link_code',
            field=models.CharField(editable=False, max_length=100, unique=True, verbose_name='Код технологического узла'),
        ),
        migrations.AlterField(
            model_name='technologicaloperation',
            name='operation_code',
            field=models.CharField(editable=False, max_length=100, unique=True, verbose_name='Код технологической операции'),
        ),
    ]
