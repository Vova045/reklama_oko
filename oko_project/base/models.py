from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db import models

class Folder(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название папки")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subfolders', verbose_name="Родительская папка")
    folder_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="Тип папки")  # например, "Операции", "Изделия", "Калькуляции"

    class Meta:
        verbose_name = "Папка"
        verbose_name_plural = "Папки"

    def __str__(self):
        return self.name
    
class FolderItem(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, verbose_name="Папка")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Элемент папки"
        verbose_name_plural = "Элементы папок"

    def __str__(self):
        return f"{self.content_object} в папке {self.folder.get_full_path()}"
    

class MeasureUnit(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    measure_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Наименование единицы измерения")

    def __str__(self):
        return self.measure_name
    
    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"

class Formulas(models.Model):
    formula_name = models.CharField(max_length=100, unique=True, verbose_name="Представление в формуле")

    def __str__(self):
        return self.formula_name

    class Meta:
        verbose_name = "Формула"
        verbose_name_plural = "Формулы"

class ParametersOfProducts(models.Model):
    parameters_product = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование параметра изделия")
    formula_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Представление в формуле")
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Единица измерения")
    formula = models.CharField(max_length=100, blank=True, null=True, verbose_name="Формула расчета")
    
    def __str__(self):
        return self.parameters_product

    class Meta:
        verbose_name = "Параметр изделия"
        verbose_name_plural = "Параметры изделия"

class Product(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    product_code = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Код изделия")
    product_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование изделия")

    def save(self, *args, **kwargs):
        if not self.product_code:  # Генерируем product_code только если его нет
            super().save(*args, **kwargs)  # Сохраняем объект для получения id
            self.product_code = f"PRD-{self.id}"  # Формируем код изделия на основе id
        super().save(*args, **kwargs)  # Сохраняем объект снова с установленным product_code

    def __str__(self):
        return self.product_name or "Unknown Product"

    class Meta:
        verbose_name = "Изделие"
        verbose_name_plural = "Изделия"

class TechnologicalLink(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    operation_link_code = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Код технологического узла")
    operation_link_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование технологического узла")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='Местонахождение', verbose_name="Родитель")

    def save(self, *args, **kwargs):
        if not self.operation_link_code: 
            super().save(*args, **kwargs) 
            self.operation_link_code = f"TECHLINK-{self.id}"  
        super().save(*args, **kwargs) 

    def __str__(self):
        return self.operation_link_name or "Неизвестная технологическая операция"

    class Meta:
        verbose_name = "Технический узел"
        verbose_name_plural = "Технические узлы"

class Nomenklatura(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    nomenklatura_code = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Код номенклатуры")
    nomenklatura_name = models.CharField(max_length=400, blank=True, null=True, verbose_name="Наименование коменклатуры")
    full_name = models.CharField(max_length=400, blank=True, null=True, verbose_name="Полное наименование")
    measure_unit = models.ForeignKey(MeasureUnit, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Единица измерения")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='Местонахождение', verbose_name="Родитель")
    comment = models.CharField(max_length=400, blank=True, null=True, verbose_name="Комментарий")
    waste_rate = models.CharField(max_length=400, blank=True, null=True, verbose_name="Норма отходов")
    material_markup = models.CharField(max_length=400, blank=True, null=True, verbose_name="Наценка материала")
    price = models.CharField(max_length=400, blank=True, null=True, verbose_name="Цена номернклатуры")

    def __str__(self):
        return self.nomenklatura_name
    
    def save(self, *args, **kwargs):
        if not self.nomenklatura_code or self.nomenklatura_code.startswith("TEMP-"):
            super().save(*args, **kwargs)  # Сохраняем объект, чтобы получить ID
            self.nomenklatura_code = f"NUM-{self.id}"  # Создаем уникальный код с использованием ID
            kwargs['force_update'] = True  # Заставляем обновить существующий объект
        super().save(*args, **kwargs)  # Сохраняем объект с новым кодом

    class Meta:
        verbose_name = "Номенклатура"
        verbose_name_plural = "Номенклатура"

class TechnologicalOperation(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    operation_code = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Код технологической операции")
    operation_link_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование технологической операции")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='Местонахождение', verbose_name="Родитель")
    formula_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Представление в формуле")
    formula = models.CharField(max_length=100, blank=True, null=True, verbose_name="Формула расчета")

    def save(self, *args, **kwargs):
        if not self.operation_code or self.operation_code.startswith("TEMP-"):
            super().save(*args, **kwargs)  # Сохраняем объект, чтобы получить ID
            self.operation_code = f"TO-{self.id}"  # Создаем уникальный код с использованием ID
            kwargs['force_update'] = True  # Заставляем обновить существующий объект
        super().save(*args, **kwargs)  # Сохраняем объект с новым кодом

    def __str__(self):
        return self.operation_link_name or "Неизвестная технологическая операция"

    class Meta:
        verbose_name = "Технологическая операция"
        verbose_name_plural = "Технологические операции"

class ProductComposition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Изделие")
    technology = models.ForeignKey(TechnologicalLink, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Технология")
    operation = models.ForeignKey(TechnologicalOperation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Технологическая операция")
    nomenclature = models.ForeignKey(Nomenklatura, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Номенклатура")
    default_selected = models.BooleanField(default=False, verbose_name="Выбран по умолчанию")

    def __str__(self):
        return f"{self.product} - {self.operation}" if self.product else "Неизвестный состав изделия"

    class Meta:
        verbose_name = "Состав изделия"
        verbose_name_plural = "Составы изделий"


class TechnologicalLinkComposition(models.Model):
    technical_link = models.ForeignKey(TechnologicalLink, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Технологический узел")
    technical_operation = models.ManyToManyField(TechnologicalOperation, blank=True, verbose_name="Технологическая операция")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('order',)
        verbose_name = "Состав технологического узла"
        verbose_name_plural = "Составы технологического узла"

class ChapterCalculation(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    chapter_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Наименование Раздела калькуляции")
    chapter_code = models.CharField(max_length=100, unique=True, editable=False, verbose_name="Код Раздела калькуляции")

    def __str__(self):
        return self.chapter_name or "Неизвестная калькуляция"
    
    def save(self, *args, **kwargs):
        if not self.chapter_code: 
            super().save(*args, **kwargs) 
            self.chapter_code = f"CHAP-{self.id}"  
        super().save(*args, **kwargs) 

    class Meta:
        verbose_name = "Раздел калькуляции"
        verbose_name_plural = "Разделы калькуляции"

class MaterialsTechnologicalOperation(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    technicological_operation = models.ForeignKey(TechnologicalOperation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Технологическая операция")
    nomenklatura = models.ForeignKey(Nomenklatura, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Номенклатура")
    chapter_calculation = models.ForeignKey(ChapterCalculation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Раздел Калькуляции")
    formula = models.CharField(max_length=100, blank=True, null=True, verbose_name="Формула")
    formula_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Представление в формуле")

    
    class Meta:
        verbose_name = "Материал технологической операции"
        verbose_name_plural = "Материалы технологической операции"

class AddingMaterialsTechnologicalOperation(models.Model):
    id = models.AutoField(primary_key=True)  # Automatically generated identifier
    technicological_operation = models.ForeignKey(TechnologicalOperation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Технологическая операция")
    nomenklatura = models.ForeignKey(Nomenklatura, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Номенклатура")
    formula = models.CharField(max_length=100, blank=True, null=True, verbose_name="Формула расчета")
    chapter_calculation = models.ForeignKey(ChapterCalculation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Раздел Калькуляции")
    formula_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Представление в формуле")

    class Meta:
        verbose_name = "Добавочный материал Технологической операции"
        verbose_name_plural = "Добавочные материалы Технологической операции"

class JopTitles(models.Model):
    id = models.AutoField(primary_key=True)
    job_title_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Наименование должности сотрудника')
    salary = models.PositiveIntegerField(default=200)
    def __str__(self):
        return self.job_title_name
    
    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"


class ProductionOperation(models.Model):
    id = models.AutoField(primary_key=True)
    operation_code = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name="Код операции производства")
    operation_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Наименование операции производства')
    job_title = models.ForeignKey('JopTitles', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Должность")
    measure_unit = models.ForeignKey('MeasureUnit', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Единица измерения")
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Папка")

    def save(self, *args, **kwargs):
        # Сначала проверка, если код не задан, то сохраняем с его генерацией
        if not self.operation_code:
            super().save(*args, **kwargs)  # Сохранение для генерации ID
            self.operation_code = f"PO-{self.id}"
            self.save(update_fields=['operation_code'])  # Сохранение только operation_code
        else:
            super().save(*args, **kwargs)  # Простое сохранение при обновлении других полей

        # Добавление записи в FolderItem, если указана папка
        if self.folder:
            operation_content_type = ContentType.objects.get_for_model(ProductionOperation)
            FolderItem.objects.update_or_create(
                folder=self.folder,
                content_type=operation_content_type,
                object_id=self.id,
                defaults={'folder': self.folder}
            )

    class Meta:
        verbose_name = "Операция производства"
        verbose_name_plural = "Операции производства"

    def __str__(self):
        return self.operation_name

class OperationOfTechnologicalOperation(models.Model):
    id = models.AutoField(primary_key=True)
    technicological_operation = models.ForeignKey(TechnologicalOperation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Технологическая операция")
    production_operation = models.ForeignKey(ProductionOperation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Операция производства")
    formula = models.CharField(max_length=100, blank=True, null=True, verbose_name="Формула расчета")
    formula_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Представление в формуле")

    class Meta:
        verbose_name = "Операция внутри Технологической операции"
        verbose_name_plural = "Операции внутри Технологической операции"

    def __str__(self):
        return f"{self.production_operation} - {self.technicological_operation}"
    
class ProductionOperationTariffs(models.Model):
    id = models.AutoField(primary_key=True)
    production_operation = models.ForeignKey(ProductionOperation, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Операция производства")
    lead_time = models.CharField(max_length=100, blank=True, null=True, verbose_name="Время выполнения")
    min_time = models.CharField(max_length=100, blank=True, null=True, verbose_name="Минимальное время")
    preporation_time = models.CharField(max_length=100, blank=True, null=True, verbose_name="Время на подготовку")
    many_people = models.CharField(max_length=100, blank=True, null=True, verbose_name="Количество человек")
    accept_each_product = models.BooleanField(default=False, verbose_name="Применять время подготовки на каждое изделие")

    class Meta:
        verbose_name = "Тариф операции производства"
        verbose_name_plural = "Тарифы операции производства"

class ParametersNormatives(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Изделие")
    overheads = models.CharField(max_length=100, blank=True, null=True, verbose_name="Накладные расходы")
    salary_fund = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фонд зарплаты")
    profit = models.CharField(max_length=100, blank=True, null=True, verbose_name="Прибыль")

    class Meta:
        verbose_name = "Параметр и Норма"
        verbose_name_plural = "Параметры и нормы"


class Calculation(models.Model):
    id = models.AutoField(primary_key=True)
    calculation_code = models.CharField(max_length=100, unique=True, editable=False, verbose_name='Код калькуляции')
    calculation_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Наименование калькуляции')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.calculation_name or "Неизвестная калькуляция"
    def save(self, *args, **kwargs):
        if not self.calculation_code: 
            super().save(*args, **kwargs) 
            self.calculation_code = f"CAL-{self.id}"  
        super().save(*args, **kwargs) 

    class Meta:
        verbose_name = "Калькуляция"
        verbose_name_plural = "Калькуляции"


class CalculationComposition(models.Model):
    calculation = models.ForeignKey(Calculation, on_delete=models.CASCADE, verbose_name='Калькуляция')
    technological_link = models.ForeignKey(TechnologicalLink, on_delete=models.CASCADE, verbose_name='Технологический узел')
    technological_operation = models.ForeignKey(TechnologicalOperation, on_delete=models.CASCADE, verbose_name='Технологическая операция')
    nomenclature = models.ForeignKey(Nomenklatura, on_delete=models.CASCADE, verbose_name='Номенклатура')
    production_operation = models.ForeignKey(ProductionOperation, on_delete=models.CASCADE, verbose_name='Операция производства')

    def __str__(self):
        return f"{self.calculation} - {self.technological_link} - {self.technological_operation}"

    class Meta:
        verbose_name = "Состав калькуляции"
        verbose_name_plural = "Составы калькуляций"

class ProductParametersInCalculation(models.Model):
    calculation = models.ForeignKey(Calculation, on_delete=models.CASCADE, verbose_name='Калькуляция')
    parameter_name = models.CharField(max_length=255, verbose_name='Наименование параметра')
    parameter_value = models.CharField(max_length=255, verbose_name='Значение параметра')

    def __str__(self):
        return f"{self.calculation} - {self.parameter_name}: {self.parameter_value} (Количество: {self.quantity_of_products})"

    class Meta:
        verbose_name = "Параметр изделия в калькуляции"
        verbose_name_plural = "Параметры изделий в калькуляции"

class ParametersNormativesInCalculation(models.Model):
    id = models.AutoField(primary_key=True)
    calculation = models.ForeignKey(Calculation, on_delete=models.CASCADE, verbose_name='Калькуляция')
    overheads = models.CharField(max_length=100, blank=True, null=True, verbose_name="Накладные расходы", default=100)
    salary_fund = models.CharField(max_length=100, blank=True, null=True, verbose_name="Фонд зарплаты", default=69)
    profit = models.CharField(max_length=100, blank=True, null=True, verbose_name="Прибыль", default=37)
    payroll = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчисления на зарплату", default=40)

    class Meta:
        verbose_name = "Параметр и Норма в калькуляции"
        verbose_name_plural = "Параметры и нормы в калькуляции"

    def __str__(self):
        return f"{self.calculation} - {self.overheads} - {self.salary_fund}  - {self.profit}"


class BitrixUser(models.Model):
    member_id = models.CharField(max_length=255, unique=True)  # Идентификатор пользователя Bitrix
    domain = models.CharField(max_length=255)  # Домен пользователя в Bitrix
    auth_token = models.CharField(max_length=255)  # Access token для доступа к API Bitrix
    refresh_token = models.CharField(max_length=255)  # Refresh token для обновления access token
    created_at = models.DateTimeField(auto_now_add=True)  # Дата установки приложения
    updated_at = models.DateTimeField(auto_now=True)  # Дата обновления токенов

    def __str__(self):
        return f"Bitrix User {self.member_id} - Domain: {self.domain}"