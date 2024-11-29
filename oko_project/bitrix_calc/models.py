from django.db import models
from base.models import Goods, TechnologicalLink, TechnologicalOperation, Nomenklatura, OperationOfTechnologicalOperation, Folder, ParametersOfProducts
# Create your models here.

class Bitrix_Goods(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Товар")
    bitrix_goods_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование товара для Битрикс")
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Папка") 
    def __str__(self):
        return f"{self.bitrix_goods_name}" if self.goods else "Неизвестный товар Битрикс"
    
    class Meta:
        verbose_name = "Товар для Битрикс"
        verbose_name_plural = "Товар для Битрикс"

class Bitrix_GoodsComposition(models.Model):
    goods = models.ForeignKey(Bitrix_Goods, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Товар")
    technology = models.ForeignKey(TechnologicalLink, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Технология")
    techoperation = models.ForeignKey(TechnologicalOperation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Технологическая операция")
    nomenclature = models.ForeignKey(Nomenklatura, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Номенклатура")
    operation = models.ForeignKey(OperationOfTechnologicalOperation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Операция производства")
    name_type_of_goods = models.CharField(max_length=100, blank=True, null=True, verbose_name="Наименование типа товара")
    type_of_goods = models.CharField(max_length=100, blank=True, null=True, verbose_name="Тип товара")

    def __str__(self):
        return f"{self.technology.operation_link_name}"

    class Meta:
        verbose_name = "Состав товара для битрикса"
        verbose_name_plural = "Составы товаров для битрикса"


class Bitrix_GoodsParameters(models.Model):
    goods = models.ForeignKey(Bitrix_Goods, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Товар")
    name_type_of_goods = models.CharField(max_length=100, blank=True, null=True, verbose_name="Наименование типа товара")
    type_of_goods = models.CharField(max_length=100, blank=True, null=True, verbose_name="Тип товара")

    def __str__(self):
        return f"{self.goods} - {self.operation}" if self.goods else "Неизвестный состав товара"

    class Meta:
        verbose_name = "Параметр товара для битрикса"
        verbose_name_plural = "Параметры товара для битрикса"


class Bitrix_ParametersNormatives(models.Model):
    id = models.AutoField(primary_key=True)
    goods = models.ForeignKey(Bitrix_Goods, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Товар")
    overheads = models.CharField(max_length=100, blank=True, null=True, verbose_name="Накладные расходы", default=100)
    salary_fund = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фонд зарплаты", default=69)
    profit = models.CharField(max_length=100, blank=True, null=True, verbose_name="Прибыль", default=37)
    payroll = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчисления на зарплату", default=40)

    class Meta:
        verbose_name = "Параметр и Норма для товара для Битрикса"
        verbose_name_plural = "Параметры и нормы для товара для Битрикса"


class Bitrix_Deal(models.Model):
    bitrix_deal_number = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Номер сделки")

class Bitrix_Calculation(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Наименование калькуляции")
    goods = models.ForeignKey(Bitrix_Goods, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Товар")
    price_material = models.CharField(max_length=100, verbose_name="Цена за материал")
    price_add_material = models.CharField(max_length=100, verbose_name="Цена за добавочный материал")
    price_salary = models.CharField(max_length=100, verbose_name="Заработная плата")
    price_payroll = models.CharField(max_length=100, verbose_name="Отчисления на заработную плату")
    price_overheads = models.CharField(max_length=100, verbose_name="Накладные расходы")
    price_cost = models.CharField(max_length=100, verbose_name="Себестоимость")
    price_profit = models.CharField(max_length=100, verbose_name="Прибыль")
    price_salary_fund = models.CharField(max_length=100, verbose_name="Фонд заработной платы")
    price_final_price = models.CharField(max_length=100, verbose_name="Общая цена")  # Убрано editable=False


class Birtrix_Price_GoodsComposition(models.Model):
    calculation = models.ForeignKey(Bitrix_Calculation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Калькуляция")
    goods_compostion = models.ForeignKey(Bitrix_GoodsComposition, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Состав товара Битрикс для кальляции")
    price_material = models.CharField(max_length=100, verbose_name="Цена за материал")
    price_add_material = models.CharField(max_length=100, verbose_name="Цена за добавочный материал")
    price_salary = models.CharField(max_length=100, verbose_name="Заработная плата")
    price_payroll = models.CharField(max_length=100, verbose_name="Отчисления на заработную плату")
    price_overheads = models.CharField(max_length=100, verbose_name="Накладные расходы")
    price_cost = models.CharField(max_length=100, verbose_name="Себестоимость")
    price_profit = models.CharField(max_length=100, verbose_name="Прибыль")
    price_salary_fund = models.CharField(max_length=100, verbose_name="Фонд заработной платы")
    price_final_price = models.CharField(max_length=100, verbose_name="Общая цена")

    def __str__(self):
        return f"{self.goods_compostion.technology.operation_link_name}  - {self.goods_compostion.techoperation.operation_link_name}"


class Bitrix_GoodsParametersInCalculation(models.Model):
    calculation = models.ForeignKey(Bitrix_Calculation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Калькуляция")
    parameters = models.ForeignKey(ParametersOfProducts, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Параметры калькуляции") 
    parameter_value = models.CharField(max_length=255, verbose_name='Значение параметра')

    def __str__(self):
        return f"{self.calculation} - {self.parameters}: {self.parameter_value}"

    class Meta:
        verbose_name = "Параметр товара для Битрикса в калькуляции"
        verbose_name_plural = "Параметры товара для Битрикса в калькуляции"

class Bitrix_Calculation_ParametersNormatives(models.Model):
    id = models.AutoField(primary_key=True)
    calculation = models.ForeignKey(Bitrix_Calculation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Калькуляция")
    overheads = models.CharField(max_length=100, blank=True, null=True, verbose_name="Накладные расходы", default=100)
    salary_fund = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фонд зарплаты", default=69)
    profit = models.CharField(max_length=100, blank=True, null=True, verbose_name="Прибыль", default=37)
    payroll = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчисления на зарплату", default=40)

    class Meta:
        verbose_name = "Параметр и Норма для товара для Калькуляции в Битриксе"
        verbose_name_plural = "Параметры и нормы для товара для Калькуляции в Битриксе"

from jsonfield import JSONField
class BitrixCompany(models.Model):
    # Основные поля
    bitrix_id = models.BigIntegerField(unique=True, db_index=True)  # ID компании в Bitrix24
    title = models.CharField(max_length=255, verbose_name="Название компании")
    company_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Тип компании")
    industry = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отрасль")
    revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name="Доход")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")

    # Контактная информация
    phone = JSONField(blank=True, null=True, verbose_name="Телефоны")  # JSON-структура для хранения телефонов
    email = JSONField(blank=True, null=True, verbose_name="Email-ы")  # JSON-структура для хранения email-ов

    # Ответственный менеджер
    assigned_by_id = models.BigIntegerField(blank=True, null=True, verbose_name="ID ответственного менеджера")

    # Метаданные
    date_created = models.DateTimeField(blank=True, null=True, verbose_name="Дата создания")
    date_modified = models.DateTimeField(blank=True, null=True, verbose_name="Дата изменения")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Компания (Bitrix)"
        verbose_name_plural = "Компании (Bitrix)"
        ordering = ["-date_created"]