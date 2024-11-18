from django.db import models
from base.models import Goods, TechnologicalLink, TechnologicalOperation, Nomenklatura, OperationOfTechnologicalOperation, Folder
# Create your models here.

class Bitrix_Goods(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Товар")
    bitrix_goods_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование товара для Битрикс")
    price_material = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Цена за материал")
    price_add_material = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Цена за добавочный материал")
    price_salary = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Заработная плата")
    price_payroll = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Отчисления на заработную плату")
    price_overheads = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Накладные расходы")
    price_cost = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Себестоимость")
    price_profit = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Прибыль")
    price_salary_fund = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Фонд заработной платы")
    price_final_price = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Общая цена")
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
        return f"{self.goods} - {self.operation}" if self.goods else "Неизвестный состав товара"

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

class Bitrix_GoodsParametersInCalculation(models.Model):
    goods = models.ForeignKey(Bitrix_Goods, on_delete=models.CASCADE, verbose_name='Товар')
    parameter_name = models.CharField(max_length=255, verbose_name='Наименование параметра')
    parameter_value = models.CharField(max_length=255, verbose_name='Значение параметра')

    def __str__(self):
        return f"{self.calculation} - {self.parameter_name}: {self.parameter_value} (Количество: {self.quantity_of_products})"

    class Meta:
        verbose_name = "Параметр товара для Битрикса в калькуляции"
        verbose_name_plural = "Параметры товара для Битрикса в калькуляции"

class Bitrix_ParametersNormatives(models.Model):
    id = models.AutoField(primary_key=True)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Товар")
    overheads = models.CharField(max_length=100, blank=True, null=True, verbose_name="Накладные расходы", default=100)
    salary_fund = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фонд зарплаты", default=69)
    profit = models.CharField(max_length=100, blank=True, null=True, verbose_name="Прибыль", default=37)
    payroll = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчисления на зарплату", default=40)

    class Meta:
        verbose_name = "Параметр и Норма для товара для Битрикса"
        verbose_name_plural = "Параметры и нормы для товара для Битрикса"


class Birtrix_Price_GoodsComposition(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Товар")
    bitrix_goods_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование товара для Битрикс")
    price_material = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Цена за материал")
    price_add_material = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Цена за добавочный материал")
    price_salary = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Заработная плата")
    price_payroll = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Отчисления на заработную плату")
    price_overheads = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Накладные расходы")
    price_cost = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Себестоимость")
    price_profit = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Прибыль")
    price_salary_fund = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Фонд заработной платы")
    price_final_price = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Общая цена")


    def save(self, *args, **kwargs):
        if not self.goods_code:  # Генерируем product_code только если его нет
            super().save(*args, **kwargs)  # Сохраняем объект для получения id
            self.goods_code = f"BIT_GOOD-{self.id}"  # Формируем код изделия на основе id
        super().save(*args, **kwargs)  # Сохраняем объект снова с установленным product_code

    def __str__(self):
        return self.goods_name or "Неизвестный товар"

    class Meta:
        verbose_name = "Цена товара для Битрикса"
        verbose_name_plural = "Цены товара для Битрикса"
