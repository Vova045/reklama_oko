from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import (
    MeasureUnit,
    Product,
    TechnologicalLink,
    Nomenklatura,
    TechnologicalOperation,
    ProductComposition,
    TechnologicalLinkComposition,
    ChapterCalculation,
    MaterialsTechnologicalOperation,
    AddingMaterialsTechnologicalOperation,
    JopTitles,
    ProductionOperation,
    OperationOfTechnologicalOperation,
    ProductionOperationTariffs,
    ParametersNormatives,
    Formulas,
    ParametersOfProducts,
    ParametersNormativesInCalculation,
    Folder, FolderItem
)
from django import forms
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from .models import ParametersNormativesInCalculation
from .forms import ParametersNormativesForm
from django.utils.translation import gettext_lazy as _
import json
from .admin_widgets import HierarchicalFolderWidget  # Импортируем виджет


@admin.register(MeasureUnit)
class MeasureUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'measure_name')
    search_fields = ('measure_name',)

class ProductCompositionInline(admin.TabularInline):
    model = ProductComposition
    extra = 1
    fields = ('technology', 'operation', 'nomenclature', 'default_selected')
    verbose_name = "Состав изделия"
    verbose_name_plural = "Составы изделий"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Добавляем классы для селекторов
        formset.form.base_fields['operation'].widget.attrs.update({'class': 'operation-select'})
        formset.form.base_fields['nomenclature'].widget.attrs.update({'class': 'nomenclature-select', 'disabled': 'disabled'})
        return formset

    class Media:
        js = ('admin/js/filter_nomenclature.js',)



# Настраиваем админ-класс для Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name')
    inlines = [ProductCompositionInline]  # Включаем inline модель в админ-панель

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)  # Путь к вашему CSS файлу
        }

    def save_model(self, request, obj, form, change):
        if not obj.product_code:
            super().save_model(request, obj, form, change)
            obj.product_code = f"PRD-{obj.id}"
            obj.save()
        else:
            super().save_model(request, obj, form, change)

class TechnologicalLinkCompositionInline(admin.TabularInline):
    model = TechnologicalLinkComposition
    extra = 1  # Количество пустых форм, которые будут отображаться


@admin.register(TechnologicalLink)
class TechnologicalLinkAdmin(admin.ModelAdmin):
    list_display = ('operation_link_code', 'operation_link_name', 'parent')
    search_fields = ('operation_link_code', 'operation_link_name')
    list_filter = ('parent',)
    actions = ['duplicate_selected']
    inlines = [TechnologicalLinkCompositionInline]  # Добавляем инлайн для TechnologicalLinkComposition

    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.id = None  # Обнуляем ID, чтобы создать новый объект
            obj.operation_link_code = None  # Устанавливаем код операции в None, чтобы он был сгенерирован заново
            obj.save()  # Первое сохранение для генерации нового ID
            obj.operation_link_code = f"TECHLINK-{obj.id}"  # Обновляем код операции с использованием нового ID
            obj.save()  # Сохраняем объект с обновленным кодом
        self.message_user(request, _("Selected items were duplicated successfully."))

    duplicate_selected.short_description = _("Копирование элемента")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (actions['delete_selected'][0],
                                          'delete_selected',
                                          _('Удалить выбранные элементы'))
        return actions

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Создаем объект TechnologicalLinkComposition при создании TechnologicalLink
        if not change:  # Если объект только что создан
            TechnologicalLinkComposition.objects.create(
                technical_link=obj,
                order=1  # Укажите нужное значение для order
            )

class NomenklaturaForm(forms.ModelForm):
    class Meta:
        model = Nomenklatura
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['folder'].queryset = Folder.objects.filter(folder_type='Номенклатура')
        self.fields['folder'].widget = HierarchicalFolderWidget()
        self.fields['folder'].widget.update_choices(self.fields['folder'].queryset)  # Обновляем опции для иерархии


@admin.register(Nomenklatura)
class NomenklaturaAdmin(admin.ModelAdmin):
    list_display = ('nomenklatura_code', 'nomenklatura_name', 'measure_unit', 'price')
    search_fields = ('nomenklatura_code', 'nomenklatura_name', 'full_name')
    list_filter = ('measure_unit',)
    exclude = ('nomenklatura_code',)
    form = NomenklaturaForm
    actions = ['duplicate_selected']

    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.id = None  # Обнуляем ID, чтобы создать новый объект
            obj.nomenklatura_code = None  # Устанавливаем код номенклатуры в None, чтобы он был сгенерирован заново
            obj.save()  # Первое сохранение для генерации нового ID
            obj.nomenklatura_code = f"NUM-{obj.id}"  # Обновляем код номенклатуры с использованием нового ID
            obj.save()  # Сохраняем объект с обновленным кодом
        self.message_user(request, _("Selected items were duplicated successfully."))

    duplicate_selected.short_description = _("Копирование элемента")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (actions['delete_selected'][0], 
                                          'delete_selected', 
                                          _('Удалить выбранные элементы'))
        return actions

class OperationOfTechnologicalOperationInline(admin.TabularInline):
    model = OperationOfTechnologicalOperation
    extra = 1  # Количество пустых полей для добавления
    fields = ['production_operation', 'formula']  # Поля, которые хотите видеть
    fk_name = 'technicological_operation'  # Поле, которое связывает с основной моделью

from django import forms
from .models import AddingMaterialsTechnologicalOperation, Folder, Nomenklatura

class AddingMaterialsTechnologicalOperationInline(admin.TabularInline):
    model = AddingMaterialsTechnologicalOperation
    extra = 0
    fields = ['nomenklatura', 'chapter_calculation', 'formula']
    fk_name = 'technicological_operation'


class MaterialsTechnologicalOperationForm(forms.ModelForm):
    folder = forms.ModelChoiceField(
        queryset=Folder.objects.filter(folder_type="Номенклатура"),
        required=False,
        label="Папка Номенклатуры"
    )

    class Meta:
        model = MaterialsTechnologicalOperation
        fields = ['folder', 'nomenklatura', 'chapter_calculation', 'formula']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если уже есть выбранная номенклатура, обновляем папку
        if self.instance and self.instance.nomenklatura:
            nomenklatura = self.instance.nomenklatura
            # Находим папку, соответствующую выбранной номенклатуре
            folder = nomenklatura.folder
            self.fields['folder'].initial = folder  # Устанавливаем начальное значение для поля папки
        
        self.fields['folder'].queryset = Folder.objects.filter(folder_type='Номенклатура')
        self.fields['folder'].widget = HierarchicalFolderWidget()
        self.fields['folder'].widget.update_choices(self.fields['folder'].queryset)  # Обновляем опции для иерархии


class MaterialsTechnologicalOperationInline(admin.TabularInline):
    model = MaterialsTechnologicalOperation
    form = MaterialsTechnologicalOperationForm
    extra = 0
    fields = ['folder', 'nomenklatura', 'chapter_calculation', 'formula']
    show_delete = True  # Это позволяет отображать чекбокс для удаления объектов
    class Media:
        js = ('admin/js/nomenklatura_filter.js',)


from django.core.exceptions import ValidationError

from django import forms

class TechnologicalOperationForm(forms.ModelForm):
    class Meta:
        model = TechnologicalOperation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем только папки с типом 'Технологические операции'
        self.fields['folder'].queryset = Folder.objects.filter(folder_type='Технологические операции')
        self.fields['folder'].widget = HierarchicalFolderWidget()
        self.fields['folder'].widget.update_choices(self.fields['folder'].queryset)  # Обновляем опции для иерархии

from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

@admin.register(TechnologicalOperation)
class TechnologicalOperationAdmin(admin.ModelAdmin):
    form = TechnologicalOperationForm
    list_display = ('operation_code', 'operation_link_name', 'folder')
    search_fields = ('operation_code', 'operation_link_name')
    list_filter = ('folder',)
    readonly_fields = ('available_formulas', 'available_math_symbols')
    exclude = ('operation_code',)
    inlines = [
        OperationOfTechnologicalOperationInline,
        AddingMaterialsTechnologicalOperationInline,
        MaterialsTechnologicalOperationInline,
    ]

    class Media:
        js = ('admin/js/copy_formula.js',)

    actions = ['duplicate_selected', 'delete_materialstechnologicaloperation']

    def available_formulas(self, obj):
        formulas = Formulas.objects.values_list('formula_name', flat=True)
        formulas_list = [f'<span class="formula-item" style="cursor: pointer;">{formula}</span>' for formula in formulas]
        return mark_safe(", ".join(formulas_list)) if formulas else "Нет доступных формул"
    available_formulas.short_description = 'Список всех формул'

    def available_math_symbols(self, obj):
        symbols = [' + ', ' - ', ' * ', ' / ', ' ( ', ' ) ']
        symbols_list = [f'<span class="math-symbol" style="cursor: pointer;">{symbol}</span>' for symbol in symbols]
        return mark_safe(", ".join(symbols_list))
    available_math_symbols.short_description = 'Список всех математических знаков'

    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.id = None  # Обнуляем ID, чтобы создать новый объект
            obj.operation_code = None  # Устанавливаем код в None для генерации нового ID
            obj.save()  # Сохраняем объект для генерации нового ID
            # Генерируем новый код в формате TO_{id}
            new_code = f"TO-{obj.id}"
            if TechnologicalOperation.objects.filter(operation_code=new_code).exists():
                pass
            else:
                obj.operation_code = new_code  # Устанавливаем уникальный код
                obj.save()  # Сохраняем объект с новым кодом

        self.message_user(request, _("Выбранные элементы были успешно дублированы."))

    duplicate_selected.short_description = _("Копировать выбранные элементы")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (actions['delete_selected'][0], 
                                          'delete_selected', 
                                          _('Удалить выбранные элементы'))
        return actions


    def save(self, *args, **kwargs):
        # Проверяем, что это новый объект
        if not self.id:  # Если ID не установлен, значит это новый объект
            super().save(*args, **kwargs)  # Сохраняем объект, чтобы получить ID
            self.operation_code = f"TO-{self.id}"  # Создаем уникальный код с использованием ID
            
        # Проверяем, уникален ли operation_code
        
        # Сохраняем объект с новым кодом, если он был установлен
        super().save(*args, **kwargs)  # Сохраняем объект с новым кодом

@admin.register(ProductComposition)
class ProductCompositionAdmin(admin.ModelAdmin):
    list_display = ('product', 'technology', 'operation', 'nomenclature', 'default_selected')
    search_fields = ('product__product_name', 'operation__operation_link_name')
    list_filter = ('default_selected',)

class TechnologicalLinkCompositionAdmin(admin.ModelAdmin):
    list_display = ('technical_link', 'get_technological_operations', 'order')
    list_filter = ('technical_link',)

    def get_technological_operations(self, obj):
        return ", ".join([operation.operation_link_name for operation in obj.technical_operation.all()])
    get_technological_operations.short_description = "Технологическая операция"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Изменяем поле для выбора технологических операций
        form.base_fields['technical_operation'].queryset = TechnologicalOperation.objects.all()
        return form

admin.site.register(TechnologicalLinkComposition, TechnologicalLinkCompositionAdmin)

@admin.register(ChapterCalculation)
class ChapterCalculationAdmin(admin.ModelAdmin):
    list_display = ('chapter_code', 'chapter_name')
    search_fields = ('chapter_code', 'chapter_name')

@admin.register(MaterialsTechnologicalOperation)
class MaterialsTechnologicalOperationAdmin(admin.ModelAdmin):
    list_display = ('technicological_operation', 'nomenklatura', 'chapter_calculation')
    search_fields = ('formula',)
    list_filter = ('chapter_calculation',)

    actions = ['duplicate_selected']

    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.id = None  # Обнуляем ID, чтобы создать новый объект
            obj.save()  # Сохраняем дубликат, который сгенерирует новый ID
        self.message_user(request, _("Selected items were duplicated successfully."))

    duplicate_selected.short_description = _("Копировать выбранные элементы")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (actions['delete_selected'][0], 
                                          'delete_selected', 
                                          _('Удалить выбранные элементы'))
        return actions

@admin.register(AddingMaterialsTechnologicalOperation)
class AddingMaterialsTechnologicalOperationAdmin(admin.ModelAdmin):
    list_display = ('technicological_operation', 'nomenklatura', 'formula', 'chapter_calculation')
    search_fields = ('formula',)
    list_filter = ('chapter_calculation',)

@admin.register(JopTitles)
class JopTitlesAdmin(admin.ModelAdmin):
    list_display = ('job_title_name',)
    search_fields = ('job_title_name',)

@admin.register(OperationOfTechnologicalOperation)
class OperationOfTechnologicalOperationAdmin(admin.ModelAdmin):
    list_display = ('technicological_operation', 'production_operation', 'formula')
    search_fields = ('formula',)
    actions = ['duplicate_selected']
    readonly_fields = ('available_formulas', 'available_math_symbols')

    class Media:
        js = ('admin/js/copy_formula.js',)

    def available_formulas(self, obj):
        formulas = Formulas.objects.values_list('formula_name', flat=True)
        formulas_list = [f'<span class="formula-item" style="cursor: pointer;">{formula}</span>' for formula in formulas]
        return mark_safe(", ".join(formulas_list)) if formulas else "Нет доступных формул"
    available_formulas.short_description = 'Список всех формул'

    def available_math_symbols(self, obj):
        symbols = [' + ', ' - ', ' * ', ' / ', ' ( ', ' ) ']
        symbols_list = [f'<span class="math-symbol" style="cursor: pointer;">{symbol}</span>' for symbol in symbols]
        return mark_safe(", ".join(symbols_list))
    available_math_symbols.short_description = 'Список всех математических знаков'

    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.id = None  # Обнуляем ID, чтобы создать новый объект
            obj.save()  # Первое сохранение для генерации нового ID
            obj.save()  # Сохраняем объект с новым ID
        self.message_user(request, _("Selected items were duplicated successfully."))

    duplicate_selected.short_description = _("Копирование операции")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (actions['delete_selected'][0],
                                          'delete_selected',
                                          _('Удалить выбранные операции'))
        return actions



@admin.register(ProductionOperationTariffs)
class ProductionOperationTariffsAdmin(admin.ModelAdmin):
    list_display = ('production_operation', 'lead_time', 'min_time', 'preporation_time', 'many_people', 'accept_each_product')
    search_fields = ('production_operation__operation_name', 'lead_time', 'min_time', 'preporation_time', 'many_people')
    
    # Определение действий
    actions = ['duplicate_selected']

    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.id = None  # Обнуляем ID для создания нового объекта
            obj.save()  # Сохраняем дубликат с новым ID
        self.message_user(request, _("Selected tariffs were duplicated successfully."))

    duplicate_selected.short_description = _("Копировать выбранные тарифы")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                _('Удалить выбранные тарифы')
            )
        return actions

@admin.register(ParametersNormatives)
class ParametersNormativesAdmin(admin.ModelAdmin):
    list_display = ('product', 'overheads', 'salary_fund', 'profit')
    search_fields = ('product__product_name',)
    
    class Media:
        js = ('admin/js/custom_admin.js',) 


@admin.register(Formulas)
class FormulasAdmin(admin.ModelAdmin):
    list_display = ('id','formula_name')

from django.utils.safestring import mark_safe

@admin.register(ParametersOfProducts)
class ParametersOfProductsAdmin(admin.ModelAdmin):
    list_display = ('parameters_product','formula_name', 'formula')
    readonly_fields = ('available_formulas','available_math_symbols')

    class Media:
        js = ('admin/js/copy_formula.js',) 
        css = {
            'all': ('admin/css/custom_admin.css',)  # Путь к вашему CSS файлу
        }
    def available_formulas(self, obj):
        formulas = Formulas.objects.values_list('formula_name', flat=True)
        formulas_list = [f'<span class="formula-item" style="cursor: pointer;">{formula}</span>' for formula in formulas]
        return mark_safe(", ".join(formulas_list)) if formulas else "Нет доступных формул"
    available_formulas.short_description = 'Список всех формул'

    def available_math_symbols(self, obj):
        symbols = [' + ', ' - ', ' * ', ' / ',' ( ', ' ) ']
        symbols_list = [f'<span class="math-symbol" style="cursor: pointer;">{symbol}</span>' for symbol in symbols]
        return mark_safe(", ".join(symbols_list))
    available_math_symbols.short_description = 'Список всех математических знаков'

from django.urls import path
from django.shortcuts import render, redirect
from .models import Calculation, TechnologicalLink, Product, ProductParametersInCalculation

@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ('calculation_code', 'calculation_name', 'created_at')


    def get_default_parameters_normatives(self):
        return {
        'overheads': ParametersNormativesInCalculation._meta.get_field('overheads').default,
        'salary_fund': ParametersNormativesInCalculation._meta.get_field('salary_fund').default,
        'profit': ParametersNormativesInCalculation._meta.get_field('profit').default,
    }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        self.prepare_context_data(request)
        return form

    def prepare_context_data(self, request):
        request.products = Product.objects.all()
        request.product_compositions = ProductComposition.objects.all()
        request.technological_links = TechnologicalLink.objects.all()
        request.technological_operations = TechnologicalOperation.objects.all()
        request.materials_technological_operation = MaterialsTechnologicalOperation.objects.all()

    def add_view(self, request, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
        self.prepare_context_data(request)
        extra_context['products'] = request.products
        extra_context['product_compositions'] = request.product_compositions
        extra_context['technological_links'] = request.technological_links
        extra_context['technological_operations'] = request.technological_operations
        extra_context['materials_technological_operation'] = request.materials_technological_operation

        # Добавляем значения по умолчанию для параметров
        extra_context.update(self.get_default_parameters_normatives())
        
        return super().add_view(request, form_url, extra_context=extra_context) 

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
        self.prepare_context_data(request)
        extra_context['products'] = request.products
        extra_context['product_compositions'] = request.product_compositions
        extra_context['technological_links'] = request.technological_links
        extra_context['technological_operations'] = request.technological_operations
        extra_context['materials_technological_operation'] = request.materials_technological_operation

        # Добавляем значения по умолчанию для параметров
        extra_context.update(self.get_default_parameters_normatives())  

        return super().change_view(request, object_id, form_url, extra_context=extra_context)
from django.contrib import admin
from .models import ParametersNormativesInCalculation
from django.urls import path
from .views import edit_default_parameters

class DefaultParametersAdmin(admin.ModelAdmin):
    change_form_template = 'admin/change_default_parameters.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('edit-default-parameters/', self.admin_site.admin_view(self.edit_default_parameters), name='edit-default-parameters-admin'),
        ]
        return custom_urls + urls

    def edit_default_parameters(self, request):
        return edit_default_parameters(request)  # Передаем управление функции
from django.contrib import admin
from .models import Folder
from .forms import FolderAdminForm  # Импортируйте вашу форму

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    form = FolderAdminForm  # Укажите вашу форму
    list_display = ('name', 'parent', 'folder_type')
    search_fields = ('name', 'folder_type')
    list_filter = ('folder_type',)
    ordering = ('name',)

    class Media:
        js = ('admin/js/folder_filter.js',)  # Путь к вашему JavaScript файлу

    def save_model(self, request, obj, form, change):
        parent_value = form.cleaned_data['parent']
        
        if parent_value == '':
            obj.parent = None  # Устанавливаем в None, если выбрано пустое значение
        else:
            obj.parent = parent_value  # Устанавливаем родительскую папку

        parent_value2 = request.POST.get('parent')
        if parent_value2 == 'null':
            parent_value = None  # или любое другое значение, которое вы используете для обозначения отсутствия родительской папки
        super().save_model(request, obj, form, change)




    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            post_data = request.POST.copy()
            parent_value = post_data.get('parent')
            if parent_value == 'null' or parent_value == '':
                post_data['parent'] = ''  # Присваиваем пустую строку для обработки в форме
            form = self.get_form(request)(post_data)
            if form.is_valid():
                if post_data['parent'] == '':
                    form.cleaned_data['parent'] = None
                else:
                    form.cleaned_data['parent'] = Folder.objects.get(id=int(post_data['parent']))
                folder = form.save(commit=False)  # Не сохраняем сразу
                folder.parent = form.cleaned_data['parent']  # Устанавливаем значение
                folder.save()  # Сохраняем объект
                self.message_user(request, "Объект успешно создан.")
                return self.response_add(request, folder)
            else:
                self.message_user(request, "Ошибка при создании объекта.", level='error')
        else:
            form = self.get_form(request)()
        queryset = Folder.objects.all().values('id', 'name', 'folder_type')
        all_folders_json = json.dumps(list(queryset))
        unique_folder_types = Folder.objects.values_list('folder_type', flat=True).distinct()
        extra_context = extra_context or {}
        extra_context['all_folders_json'] = all_folders_json
        extra_context['unique_folder_types'] = unique_folder_types
        extra_context['form'] = form
        return super().add_view(request, form_url, extra_context=extra_context)


    def change_view(self, request, object_id, form_url='', extra_context=None):
        print("Запрос POST:", request.POST)
        folder_instance = self.get_object(request, object_id)

        if request.method == 'POST':
            # Копируем POST-данные, чтобы иметь возможность изменять их
            post_data = request.POST.copy()
            
            # Получаем значение parent
            parent_value = post_data.get('parent')
            if parent_value == 'null' or parent_value == '':
                post_data['parent'] = ''  # Присваиваем пустую строку для обработки в форме
            
            # Создаем форму с измененными данными
            form = self.get_form(request)(post_data, instance=folder_instance)

            if form.is_valid():
                # Если значение parent было изменено, то присваиваем None
                if post_data['parent'] == '':
                    form.cleaned_data['parent'] = None
                else:
                    form.cleaned_data['parent'] = Folder.objects.get(id=int(post_data['parent']))
                
                # Сохраняем изменения без немедленного сохранения объекта
                folder = form.save(commit=False)
                folder.parent = form.cleaned_data['parent']
                folder.save()  # Сохраняем объект
                self.message_user(request, "Объект успешно обновлен.")
                return self.response_change(request, folder)
            else:
                print("Ошибки формы:", form.errors)  # Выводим ошибки формы
                self.message_user(request, "Ошибка при обновлении объекта.", level='error')
        else:
            form = self.get_form(request)(instance=folder_instance)

        queryset = Folder.objects.all().values('id', 'name', 'folder_type')
        all_folders_json = json.dumps(list(queryset))
        unique_folder_types = Folder.objects.values_list('folder_type', flat=True).distinct()
        extra_context = extra_context or {}
        extra_context['all_folders_json'] = all_folders_json
        extra_context['unique_folder_types'] = unique_folder_types
        extra_context['form'] = form

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

class ProductionOperationTariffsInline(admin.TabularInline):
    model = ProductionOperationTariffs
    extra = 1  # Количество пустых форм для добавления новых тарифов
    fields = ('lead_time', 'min_time', 'preporation_time', 'many_people', 'accept_each_product')

    def save_related(self, request, form, formset, change):
        # Сначала сохраняем родительский объект
        super().save_related(request, form, formset, change)
        # Теперь устанавливаем production_operation для новых тарифов
        for f in formset:
            if f.instance.pk is None:  # Если тариф новый
                f.instance.production_operation = form.instance  # Устанавливаем связь с текущей операцией
                f.save()  # Сохраняем тариф

class ProductionOperationAdminForm(forms.ModelForm):
    class Meta:
        model = ProductionOperation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['folder'].queryset = Folder.objects.filter(folder_type='Операция производства')
        self.fields['folder'].widget = HierarchicalFolderWidget()
        self.fields['folder'].widget.update_choices(self.fields['folder'].queryset)  # Обновляем опции для иерархии

@admin.register(ProductionOperation)
class ProductionOperationAdmin(admin.ModelAdmin):
    form = ProductionOperationAdminForm
    list_display = ('folder', 'operation_name', 'job_title', 'operation_code','measure_unit' )
    search_fields = ('operation_code', 'operation_name')
    list_filter = ('job_title', 'measure_unit')
    inlines = [ProductionOperationTariffsInline]  # Добавляем Inline для тарифов

    # Определяем действия
    actions = ['duplicate_selected']

    def duplicate_selected(self, request, queryset):
        for obj in queryset:
            obj.id = None  # Обнуляем ID для создания нового объекта
            obj.operation_code = None  # Устанавливаем код операции в None, чтобы он был сгенерирован заново
            obj.save()  # Первое сохранение для генерации нового ID
            obj.operation_code = f"PO-{obj.id}"  # Обновляем код операции с использованием нового ID
            obj.save()  # Сохраняем объект с обновленным кодом
        self.message_user(request, _("Selected items were duplicated successfully."))

    duplicate_selected.short_description = _("Копирование элемента")

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                'delete_selected',
                _('Удалить выбранные элементы')
            )
        return actions
    

from .models import BitrixUser

class BitrixUserAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'domain', 'auth_token', 'refresh_token')
    search_fields = ('member_id', 'domain')
    list_filter = ('domain',)

admin.site.register(BitrixUser, BitrixUserAdmin)