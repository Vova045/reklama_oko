from django.contrib import admin
from .models import ( 
    Bitrix_Goods, Bitrix_GoodsComposition, Bitrix_GoodsParameters, 
    Bitrix_ParametersNormatives, Birtrix_Price_GoodsComposition,
    Goods, Bitrix_GoodsParametersInCalculation,
)
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.shortcuts import redirect
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django import forms
from .admin_widgets import HierarchicalFolderWidget  # Импортируем виджет
from base.models import (GoodsComposition,Folder,TechnologicalLink,Nomenklatura,TechnologicalOperation,OperationOfTechnologicalOperation, ParametersOfProducts)



class Bitrix_GoodsCompositionForm(forms.ModelForm):
    class Meta:
        model = Bitrix_GoodsComposition
        fields = '__all__'

    # Для каждого поля папки создаем временные поля, чтобы фильтровать узлы
    folder_technology = forms.ModelChoiceField(
        queryset=Folder.objects.filter(folder_type='Технологические узлы'),
        required=False,
        widget=HierarchicalFolderWidget(),  # Use custom widget for hierarchical display
        label='Папка для Технологии'
    )

    folder_techoperation = forms.ModelChoiceField(
        queryset=Folder.objects.filter(folder_type='Технологические операции'),
        required=False,
        widget=HierarchicalFolderWidget(),
        label='Папка для Техоперации'
    )

    folder_nomenclature = forms.ModelChoiceField(
        queryset=Folder.objects.filter(folder_type='Номенклатура'),
        required=False,
        widget=HierarchicalFolderWidget(),
        label='Папка для Номенклатуры'
    )

    folder_operation = forms.ModelChoiceField(
        queryset=Folder.objects.filter(folder_type='Операция производства'),
        required=False,
        widget=HierarchicalFolderWidget(),
        label='Папка для Операции'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For each folder field, update the widget choices
        self.fields['folder_technology'].widget.update_choices(self.fields['folder_technology'].queryset)
        self.fields['folder_techoperation'].widget.update_choices(self.fields['folder_techoperation'].queryset)
        self.fields['folder_nomenclature'].widget.update_choices(self.fields['folder_nomenclature'].queryset)
        self.fields['folder_operation'].widget.update_choices(self.fields['folder_operation'].queryset)

        # Additional filtering for nodes (like Technologies, Techoperations, etc.)
        self.fields['technology'].queryset = TechnologicalLink.objects.all()
        self.fields['techoperation'].queryset = TechnologicalOperation.objects.all()
        self.fields['nomenclature'].queryset = Nomenklatura.objects.all()
        self.fields['operation'].queryset = OperationOfTechnologicalOperation.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        folder_technology = cleaned_data.get("folder_technology")
        # You can add additional validations if needed
        return cleaned_data



class Bitrix_GoodsForm(forms.ModelForm):
    folder = forms.ModelChoiceField(
        queryset=Folder.objects.filter(folder_type="Товар"),
        required=False,
        label="Папка Товаров"
    )

    class Meta:
        model = Bitrix_Goods
        fields = ['folder', 'bitrix_goods_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If there is an existing folder, set it as the initial value
        if self.instance and self.instance.folder:
            folder = self.instance.folder
            self.fields['folder'].initial = folder

        # Restrict queryset to only show folders of type "Изделия"
        self.fields['folder'].queryset = Folder.objects.filter(folder_type='Товар')
        self.fields['folder'].widget = HierarchicalFolderWidget()  # Custom widget for hierarchical display
        self.fields['folder'].widget.update_choices(self.fields['folder'].queryset)  # Update choices for hierarchy



class Bitrix_GoodsCompositionInline(admin.TabularInline):
    model = Bitrix_GoodsComposition
    form = Bitrix_GoodsCompositionForm  # Use the form with hierarchical fields
    extra = 0
    fields = (
        'folder_technology', 'technology',
        'techoperation',
        'nomenclature',
        'operation',
        'name_type_of_goods','type_of_goods',
    )
    verbose_name = "Состав товара"
    verbose_name_plural = "Составы товаров"

    class Media:
        js = ('admin/js/filter_goods_bitrix.js',)  # Ensure your custom JS is included

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Filter based on selected folder
        folder_technology_id = request.GET.get('folder_technology', None)
        folder_techoperation_id = request.GET.get('folder_techoperation', None)
        folder_nomenclature_id = request.GET.get('folder_nomenclature', None)
        folder_operation_id = request.GET.get('folder_operation', None)

        if folder_technology_id and db_field.name == "technology":
            kwargs['queryset'] = TechnologicalLink.objects.filter(folder_id=folder_technology_id)
        elif folder_techoperation_id and db_field.name == "techoperation":
            kwargs['queryset'] = TechnologicalOperation.objects.filter(folder_id=folder_techoperation_id)
        elif folder_nomenclature_id and db_field.name == "nomenclature":
            kwargs['queryset'] = Nomenklatura.objects.filter(folder_id=folder_nomenclature_id)
        elif folder_operation_id and db_field.name == "operation":
            kwargs['queryset'] = OperationOfTechnologicalOperation.objects.filter(folder_id=folder_operation_id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)



# Настраиваем админ-класс для Product
@admin.register(Bitrix_Goods)
class Bitrix_GoodsAdmin(admin.ModelAdmin):
    list_display = ('bitrix_goods_name',)
    inlines = [Bitrix_GoodsCompositionInline]  # Включаем inline модель в админ-панель
    form = Bitrix_GoodsForm

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # Путь к вашему CSS файлу
        }



@admin.register(Bitrix_GoodsParameters)
class Bitrix_GoodsParametersAdmin(admin.ModelAdmin):
    list_display = ('goods', 'type_of_goods', 'name_type_of_goods')
    search_fields = ('goods__bitrix_goods_name', 'type_of_goods', 'name_type_of_goods')


@admin.register(Bitrix_ParametersNormatives)
class Bitrix_ParametersNormativesAdmin(admin.ModelAdmin):
    list_display = ('goods', 'overheads', 'salary_fund', 'profit')
    search_fields = ('goods__bitrix_goods_name', 'overheads', 'salary_fund', 'profit')


class BirtrixPriceGoodsCompositionInline(admin.TabularInline):
    model = Birtrix_Price_GoodsComposition
    extra = 0  # Количество пустых форм, которые будут отображаться в интерфейсе по умолчанию
    fields = (
        'goods_compostion',
        'price_material',
        'price_add_material',
        'price_salary',
        'price_payroll',
        'price_overheads',
        'price_cost',
        'price_profit',
        'price_salary_fund',
        'price_final_price',
    )  # Поля, которые будут отображаться в админке
    verbose_name = "Состав товара для калькуляции"
    verbose_name_plural = "Составы товара для калькуляций"
    

class BitrixGoodsParametersInCalculationInline(admin.TabularInline):
    model = Bitrix_GoodsParametersInCalculation
    extra = 0
    fields = ('parameters', 'parameter_value')
    verbose_name = "Параметр калькуляции"
    verbose_name_plural = "Параметры калькуляции"


from .models import Bitrix_Calculation
from django.contrib import admin

@admin.register(Bitrix_Calculation)
class BitrixCalculationAdmin(admin.ModelAdmin):
    # Поля для отображения в списке объектов
    list_display = (
        'name', 
        'goods', 
        'price_material', 
        'price_add_material', 
        'price_salary', 
        'price_payroll', 
        'price_overheads', 
        'price_cost', 
        'price_profit', 
        'price_salary_fund', 
        'price_final_price'
    )
    
    # Поля для поиска
    search_fields = ('name', 'goods__name')
    
    # Поля для фильтрации
    list_filter = ('goods',)
    inlines = [BirtrixPriceGoodsCompositionInline, BitrixGoodsParametersInCalculationInline]
    # Поля для редактирования напрямую из списка
    list_editable = ('price_final_price',)
    
    # Поля для отображения в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'goods')
        }),
        ('Детали цен', {
            'fields': (
                'price_material', 
                'price_add_material', 
                'price_salary', 
                'price_payroll', 
                'price_overheads', 
                'price_cost', 
                'price_profit', 
                'price_salary_fund', 
                'price_final_price'
            )
        }),
    )
    
    
    # Постраничный вывод объектов
    list_per_page = 20


from django.contrib import admin
from .models import BitrixCompany

@admin.register(BitrixCompany)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'phone','bitrix_id')  # Настраиваем видимые колонки
    search_fields = ('name', 'email', 'phone')  # Поля для поиска
    readonly_fields = ('bitrix_id',)  # Поля только для чтения
