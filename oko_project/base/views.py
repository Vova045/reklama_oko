from django.http import JsonResponse
import re
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, get_object_or_404
from .models import ProductComposition, TechnologicalOperation, MaterialsTechnologicalOperation, Nomenklatura, ParametersOfProducts
from .models import MaterialsTechnologicalOperation, ParametersNormativesInCalculation, OperationOfTechnologicalOperation, ProductionOperation, ProductionOperationTariffs, TechnologicalLink, Folder
from .forms import ParametersNormativesInCalculationForm
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def home(request):
    return render(request, 'home.html')


import requests
from django.http import JsonResponse

def bitrix_proxy(request):
    access_token = request.GET.get('access_token')  # Получаем токен из запроса
    url = 'https://oko.bitrix24.ru/rest/user.current.json'  # URL Bitrix24

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({"error": response.json()}, status=response.status_code)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

@csrf_exempt
def bind_application(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)

    # Получение access_token
    access_token = request.GET.get('access_token')
    if not access_token:
        return JsonResponse({"error": "Access token is missing"}, status=400)

    # URL для добавления приложения в Bitrix24
    BASE_URL = "https://oko.bitrix24.ru/rest/placement.bind.json"

    # Данные для размещения
    payload = {
        "PLACEMENT": "left_menu",  # Левое меню — доступное почти на всех аккаунтах
        "HANDLER": "https://reklamaoko.ru",
        "TITLE": "Мое Django приложение",
        "DESCRIPTION": "Приложение для управления рекламой"
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Отправка запроса к Bitrix24
    response = requests.post(BASE_URL, headers=headers, data=json.dumps(payload))

    # Проверка ответа
    if response.status_code == 200:
        return JsonResponse({"success": "Ссылка на приложение успешно добавлена в меню!"})
    else:
        print("Ошибка при добавлении ссылки:", response.status_code, response.text)
        return JsonResponse({"error": "Ошибка при добавлении ссылки", "details": response.text}, status=response.status_code)


def get_technological_links(request):
    product_id = request.GET.get('product_id')
    
    if product_id:
        compositions = ProductComposition.objects.filter(product_id=product_id)
    else:
        compositions = []

    # Собираем уникальные ссылки
    unique_links = {}
    
    for comp in compositions:
        tech_id = comp.technology.id
        tech_name = comp.technology.operation_link_name

        # Используем id как ключ, чтобы не было дубликатов
        unique_links[(tech_id, tech_name)] = {'id': tech_id, 'name': tech_name}
    
    # Преобразуем уникальные значения обратно в список
    links = list(unique_links.values())

    return JsonResponse({'links': links})

def edit_default_parameters(self, request):
    context = {
        'opts': self.model._meta,
        'app_label': self.model._meta.app_label,
        'site_title': 'Изменить параметры по умолчанию'  # Устанавливаем новый заголовок
    }
    # Your logic for handling the default parameter update
    return render(request, 'admin/change_default_parameters.html', context)

def filter_nomenclature(request):
    operation_id = request.GET.get('operation_id')
    nomenklatura = []

    if operation_id:
        materials = MaterialsTechnologicalOperation.objects.filter(technicological_operation_id=operation_id)
        nomenklatura = [{'id': mat.nomenklatura.id, 'name': mat.nomenklatura.nomenklatura_name} for mat in materials]

    return JsonResponse({'nomenklatura': nomenklatura})

def get_technological_operations(request):
    if request.method == 'POST':
        # Получаем данные из тела POST-запроса
        data = json.loads(request.body)
        link_ids = data.get('links')  # Получаем ссылки из данных
        if link_ids and link_ids[0]: 
            link = TechnologicalLink.objects.filter(
                operation_link_name__in=link_ids
            )
            operations = TechnologicalOperation.objects.filter(
                productcomposition__technology__id__in=link
            ).distinct() 
        else:
            operations = []  # Очищаем список операций, если узлы не выбраны
        operation_list2 = [{'id': op.id, 'name': op.operation_link_name, 'formula': op.formula} for op in operations]
        operation_list = []
        for ol in operation_list2:
            x = ol['name']
            y = TechnologicalOperation.objects.filter(
                operation_link_name=x
            )
            product_compositions = ProductComposition.objects.filter(
            operation__in=y # Фильтруем по выбранным операциям
        )[0]
            operation_list.append({
                'id': ol['id'],
                'name': ol['name'],  # Предполагаем, что есть поле name у TechnologicalOperation
                'formula': ol['formula'],  # Предполагаем, что есть поле formula у TechnologicalOperation
                'link': product_compositions.technology.operation_link_name
            })
        inner_operations = [] 
        for oper in operation_list:
            y = oper['name']  # Получаем значение 'name' из словаря

            # Фильтруем объекты OperationOfTechnologicalOperation по полю technicological_operation
            matching_operations = TechnologicalOperation.objects.filter(operation_link_name=y)
            # Если найдены совпадения, выводим их
            for operation in matching_operations:  # Выводим совпадающий объект
                matching_operations2 = OperationOfTechnologicalOperation.objects.filter(technicological_operation=operation)
                for op in matching_operations2:
                    inner_operations.append(str(op.production_operation))
        return JsonResponse({'operations': operation_list, 'inner_operations': inner_operations })

def update_selected_operations(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_operations = data.get('selected_operations')
        # Извлекаем выделенные операции из POST-запроса
        print(selected_operations)
        if selected_operations and selected_operations[0]: 
            return JsonResponse({'success': True, 'selected_operations': selected_operations})
        else:
            return JsonResponse({'success': False, 'message': 'Выделенных операций нет.'})

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса.'})
def update_selected_nomenclature(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_nomenclature = data.get('selected_nomenclature')
        print(selected_nomenclature)  # Выводим выделенные номенклатуры в консоль для проверки

        if selected_nomenclature and selected_nomenclature[0]:
            return JsonResponse({'success': True, 'selected_nomenclature': selected_nomenclature})
        else:
            return JsonResponse({'success': False, 'message': 'Выделенных номенклатур нет.'})

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса.'})

def get_nomenclature(request):
    operations_ids = request.GET.get('operations', '')
    operations_ids_list = operations_ids.split(',') if operations_ids else []
    if operations_ids_list:
        techoper = TechnologicalOperation.objects.filter(
            operation_link_name__in=operations_ids_list
        ).distinct()
        
        nomenclature = MaterialsTechnologicalOperation.objects.filter(
            technicological_operation__in=techoper
        ).distinct()
    else:
        nomenclature = []
    nomenclature_list = [{'id': item.id, 'name': str(item.nomenklatura), 'technicological_operation': str(item.technicological_operation)} for item in nomenclature]
    return JsonResponse({'nomenclature': nomenclature_list})

def extract_variables(formula):
    print(formula)
    return re.findall(r'\b\w+\b', formula)
def get_all_parameters_without_formula(variable_names):
    variables_without_formula = set() 
    next_variables_to_check = set(variable_names)  
    while next_variables_to_check: 
        current_variable = next_variables_to_check.pop()
        parameter = ParametersOfProducts.objects.filter(formula_name=current_variable).first()
        if parameter and parameter.formula:
            new_variables = extract_variables(parameter.formula)
            print(new_variables)
            next_variables_to_check.update(new_variables) 
        else:
            variables_without_formula.add(current_variable)

    return variables_without_formula

def get_parameters_product(request):
    operations_ids = request.GET.get('operations', '')
    print(operations_ids)
    operations_ids = operations_ids.split(',') if operations_ids else []
    
    if operations_ids:
        # Получаем все операции, соответствующие переданным именам операций
        operations = TechnologicalOperation.objects.filter(operation_link_name__in=operations_ids)
        
        all_parameters = {}
        
        for operation in operations:
            print(operation.formula)
            if operation.formula:
                # Извлекаем переменные из формулы
                initial_variables = extract_variables(operation.formula)
                # Получаем параметры, для которых нет формулы
                variables_without_formula = get_all_parameters_without_formula(initial_variables)
                # Находим соответствующие параметры продуктов
                matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                # Добавляем параметры в словарь с проверкой уникальности по 'name'
                for item in matching_parameters:
                    if item.parameters_product not in all_parameters:
                        all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
        
        return JsonResponse({'parameters': list(all_parameters.values())})
    else:
        return JsonResponse({'parameters': []})



def save_parameters_normatives(request):
    if request.method == 'POST':
        form = ParametersNormativesInCalculationForm(request.POST)
        if form.is_valid():
            parameters_normatives = form.save()
            return JsonResponse({'success': True, 'id': parameters_normatives.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def get_nomenclature_price(request):
    data = json.loads(request.body)
    nomenclature_list = data.get('nomenclature_list')
    total_price = 0.0  # Общая цена
    nomenclature_details = []  # Список для хранения деталей по каждой номенклатуре

    if nomenclature_list:
        for num in nomenclature_list:
            nomenclature = Nomenklatura.objects.filter(nomenklatura_name=num).first()
            
            # Проверяем, был ли найден объект номенклатуры
            if nomenclature:
                try:
                    # Расчет цены с учетом норм отходов и наценки
                    price = float(nomenclature.price)
                    total_price += price  # Добавляем к общей сумме

                    # Добавляем информацию о текущей номенклатуре в список
                    nomenclature_details.append({
                        'nomenklatura_name': nomenclature.nomenklatura_name,
                        'price': f"{price:.2f}"  # Форматируем цену для каждой номенклатуры
                    })
                except (ValueError, TypeError):
                    print(f"Ошибка при расчете цены для номенклатуры: {nomenclature.nomenklatura_name}")
            else:
                print(f"Номенклатура {num} не найдена.")
    
    # Форматируем общую цену до двух знаков после запятой
    total_price = f"{total_price:.2f}"

    # Возвращаем как общую цену, так и детали по каждой номенклатуре
    return JsonResponse({
        'total_price': total_price,
        'nomenclature_details': nomenclature_details
    })


from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import ParametersOfProducts, TechnologicalOperation

@csrf_exempt
def update_parameters_product(request):
    if request.method == 'POST':
        try:
            def replace_formula_with_calculation(tech_operation):
                final_formula = tech_operation.formula  # Получаем исходную формулу операции
                
                while True:
                    initial_formula = final_formula  # Сохраняем текущую формулу для проверки изменений
                    elements = final_formula.split()  # Разделяем формулу на отдельные элементы
                    
                    # Перебираем все элементы формулы
                    for i, element in enumerate(elements):
                        try:
                            # Ищем, является ли элемент представлением
                            param_obj = ParametersOfProducts.objects.get(Q(formula_name=element))

                            if param_obj.formula:
                                # Если у представления есть формула расчета, заменяем его на формулу с учетом скобок
                                elements[i] = f" ( {param_obj.formula} ) "
                        except ParametersOfProducts.DoesNotExist:
                            # Если представление не найдено, продолжаем
                            pass

                    # Соединяем все элементы обратно в строку
                    final_formula = ' '.join(elements)

                    # Если формула не изменилась, выходим из цикла
                    if final_formula == initial_formula:
                        break

                # Обновляем значение formula у технологической операции
                tech_operation.formula = final_formula

            # Загружаем JSON данные из запроса
            data = json.loads(request.body)
            # Извлекаем параметры изделия из данных
            product_parameters = data.get('product_parameters', {})
            inner_operations = data.get('inner_operations', {})
            nomenclature_list = data.get('nomenclature_list')
            technological_operations = data.get('technological_operations', [])
            old_tech = technological_operations
            nomenclature_count = len(nomenclature_list) if nomenclature_list is not None else 0

            # Перебираем каждый параметр, чтобы сохранить или обновить его
            parameters_dict = {}
            for param_name, param_value in product_parameters.items():
                parameter = ParametersOfProducts.objects.get(parameters_product=param_name)
                parameters_dict[parameter.formula_name] = param_value
            for inner_name in inner_operations:
                
                operation = ProductionOperation.objects.filter(operation_name=inner_name).first()
                tarif = ProductionOperationTariffs.objects.filter(production_operation=operation).first()
                inner_operation = OperationOfTechnologicalOperation.objects.filter(production_operation=operation)
                for inner in inner_operation:
                    replace_formula_with_calculation(inner)
                    tokens = inner.formula.replace('*', ' * ').replace('/', ' / ').split()
                    cleaned_tokens = []

                    for i in range(len(tokens)):
                        if tokens[i] in parameters_dict:
                            tokens[i] = parameters_dict[tokens[i]]
                    for token in tokens:
                        try:
                            value = float(token)
                            cleaned_tokens.append(str(value))
                        except (ValueError, TypeError):
                            if token is None:
                                cleaned_tokens.append('0')
                            else:
                                cleaned_tokens.append(token)
                    final_formula = ' '.join(cleaned_tokens)
                    result = eval(final_formula)
                    
                    def safe_float(value):
                        try:
                            return float(value)
                        except (ValueError, TypeError):
                            return 0.0  # Возвращаем 0.0 в случае ошибки

                    # Используем безопасное преобразование
                    lead_time = safe_float(tarif.lead_time)
                    preporation_time = safe_float(tarif.preporation_time)
                    min_time = safe_float(tarif.min_time)
                    many_people = safe_float(tarif.many_people)
                    salary = safe_float(operation.job_title.salary)

                    # Проверяем условие и вычисляем result2
                    if (lead_time + preporation_time) < min_time:
                        result2 = result * ((min_time * many_people) / 60) * salary
                    else:
                        result2 = result * ((lead_time + preporation_time) * many_people / 60) * salary
                    # Умножаем на количество номенклатуры
                    result2 = result2 * nomenclature_count
                    print(f"{inner} -- Результат операции: {result2}")
                    
            
            operations_prices = []

            for operation in technological_operations:
                try:
                    # Задаем начальные значения для переменных накопления
                    total_nomenclature = 0.0
                    total_final_price = 0.0
                    
                    if isinstance(operation, str):
                        operation = [operation]
                    tech_operations = TechnologicalOperation.objects.filter(operation_link_name__in=operation)
                    
                    for tech_operation in tech_operations:
                        replace_formula_with_calculation(tech_operation)
                        tokens = tech_operation.formula.replace('*', ' * ').replace('/', ' / ').split()
                        result_tokens = []

                        for token in tokens:
                            if token in parameters_dict:
                                result_tokens.append(parameters_dict[token])
                            else:
                                result_tokens.append(token)

                        new_formula = []
                        for token in result_tokens:
                            try:
                                value = float(token)
                                new_formula.append(f"{value:.2f}")
                            except ValueError:
                                parameter = ParametersOfProducts.objects.filter(formula_name=token).first()
                                if parameter:
                                    param_value = product_parameters.get(parameter.id, 0)
                                    new_formula.append(f"{param_value:.2f}")
                                else:
                                    new_formula.append(token)

                        final_formula = ' '.join(new_formula)
                        print(final_formula)
                        try:
                            result = eval(final_formula)
                        except Exception as e:
                            print("Ошибка при вычислении формулы:", e)

                        default_parameters = ParametersNormativesInCalculation._meta.get_field('overheads').default
                        salary_fund_default = ParametersNormativesInCalculation._meta.get_field('salary_fund').default
                        profit_default = ParametersNormativesInCalculation._meta.get_field('profit').default
                        payroll_default = ParametersNormativesInCalculation._meta.get_field('payroll').default

                        materials_tech_ops = MaterialsTechnologicalOperation.objects.filter(technicological_operation=tech_operation)
                        matched_nomenklaturas = []
                        
                        for material in materials_tech_ops:
                            if material.nomenklatura and material.nomenklatura.nomenklatura_name in nomenclature_list:
                                matched_nomenklaturas.append(material.nomenklatura)

                        nomenclature_total = 0.0
                        nomenclature_price_without_percent_total = 0.0

                        for nomenclature in matched_nomenklaturas:
                            nomenclature_price = float(nomenclature.price) * float(nomenclature.waste_rate) * float(nomenclature.material_markup)
                            nomenclature_price_without_percent = float(nomenclature.price)
                            nomenclature_price_without_percent_total += nomenclature_price_without_percent
                            nomenclature_total += nomenclature_price

                        price_nomenclatura = result * nomenclature_total + result * nomenclature_total * salary_fund_default / 100 + result * nomenclature_total * profit_default / 100
                        price_operation = result + result * default_parameters / 100 + result * payroll_default / 100
                        final_price = price_nomenclatura + price_operation

                        operations_prices.append({
                            'nomenclature_without_percent': nomenclature_price_without_percent_total,
                            'nomenclature_total': nomenclature_total,
                            'operation': tech_operation.operation_link_name,
                            'result': result,
                            'price_nomenclatura': price_nomenclatura,
                            'price_operation': price_operation,
                            'final_price': final_price
                        })

                        # Суммируем значения из operations_prices
                        for op in operations_prices:
                            total_nomenclature += op['nomenclature_without_percent']
                            total_final_price += op['final_price']

                        print(f"{op['operation']} -- Результат операции: {op['final_price']}")
                    print("Сумма всех nomenclature_total:", total_nomenclature)
                    print("Сумма всех final_prices:", total_final_price)

                except Exception as e:
                    print(f"Ошибка при вычислении операции {operation}: {e}")

            response_data = {
                'success': True,
                'total_nomenclature': total_nomenclature,
                'total_final_price': total_final_price,
                'operations': operations_prices,
                'default_parameters': {
                    'overheads': default_parameters,
                    'salary_fund': salary_fund_default,
                    'profit': profit_default,
                    'payroll': payroll_default
                }
            }
            print(response_data)
            return JsonResponse(response_data)


        except Exception as e:
            print("Ошибка при обработке запроса:", e)
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'}, status=405)



from django.shortcuts import render, redirect
from .models import ParametersNormativesInCalculation
from django.contrib import messages
def edit_default_parameters(request):
    current_overheads = ParametersNormativesInCalculation._meta.get_field('overheads').default
    current_salary_fund = ParametersNormativesInCalculation._meta.get_field('salary_fund').default
    current_profit = ParametersNormativesInCalculation._meta.get_field('profit').default
    current_payroll = ParametersNormativesInCalculation._meta.get_field('payroll').default

    if request.method == 'POST':
        overheads = request.POST.get('overheads')
        salary_fund = request.POST.get('salary_fund')
        profit = request.POST.get('profit')
        payroll = request.POST.get('payroll')
        ParametersNormativesInCalculation._meta.get_field('overheads').default = overheads
        ParametersNormativesInCalculation._meta.get_field('salary_fund').default = salary_fund
        ParametersNormativesInCalculation._meta.get_field('profit').default = profit
        ParametersNormativesInCalculation._meta.get_field('payroll').default = payroll

        messages.success(request, "Значения по умолчанию успешно обновлены.")
        return redirect('edit-default-parameters')  # Используйте правильное имя маршрута


    context = {
        'current_overheads': current_overheads,
        'current_salary_fund': current_salary_fund,
        'current_profit': current_profit,
        'current_payroll': current_payroll,
    }
    return render(request, 'admin/change_default_parameters.html', context)

from django.db.models import OuterRef, Subquery
from django.http import JsonResponse

def check_folder_type(request):
    if request.method == 'POST':
        folder_type = request.POST.get('folder_type', '')

        # Получаем все папки соответствующие типу
        matching_folders = Folder.objects.filter(folder_type=folder_type)

        # Создаем словарь для хранения иерархической структуры
        folder_map = {}

        # Заполняем словарь данными о папках
        for folder in matching_folders:
            folder_map[folder.id] = {
                'id': folder.id,
                'name': folder.name,
                'parent_id': folder.parent_id,
                'children': [],
                'parent_name': folder.parent.name if folder.parent else None  # Получаем имя родителя, если есть
            }

        # Создаем иерархическую структуру
        for folder in matching_folders:
            if folder.parent_id:
                # Добавляем текущую папку как дочернюю к ее родительской
                folder_map[folder.parent_id]['children'].append(folder_map[folder.id])

        # Собираем только корневые папки (те, у кого нет родителя)
        root_folders = [folder for folder in folder_map.values() if folder['parent_id'] is None]

        all_folder_types = Folder.objects.values_list('folder_type', flat=True).distinct()

        return JsonResponse({
            'folder_type': folder_type,
            'matching_folders': root_folders,
            'all_folder_types': list(all_folder_types)
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


def load_initial_folders(request):
    if request.method == 'GET':
        folders = Folder.objects.all().select_related('parent')  # Получаем все папки с их родителями
        folder_map = {}

        # Создаем словарь, где ключ - id папки, значение - объект папки
        for folder in folders:
            folder_map[folder.id] = {
                'id': folder.id,
                'name': folder.name,
                'parent': folder.parent_id,
                'children': []
            }

        # Связываем родительские и дочерние папки
        for folder in folders:
            if folder.parent:
                folder_map[folder.parent_id]['children'].append(folder_map[folder.id])

        # Список для возвращаемых папок, включающий только корневые
        root_folders = [folder for folder in folder_map.values() if folder['parent'] is None]

        return JsonResponse({'matching_folders': root_folders})



import requests

def get_bitrix_user(request):
    # Настройки API и URL для вебхука
    BASE_URL = "https://oko.bitrix24.ru/rest/7/5c7fk7e5y2cev81a/placement.bind.json"

    # Данные для размещения
    payload = {
        "PLACEMENT": "left_menu",  # Для добавления в левое меню
        "HANDLER": "https://reklamaoko.ru",  # Ссылка на ваше Django приложение
        "TITLE": "Мое Django приложение",  # Название в меню
        "DESCRIPTION": "Приложение для управления рекламой"  # Описание
    }

    # Отправка запроса
    response = requests.post(BASE_URL, json=payload)

    # Проверка ответа
    if response.status_code == 200:
        return JsonResponse({"message": "Ссылка на приложение успешно добавлена в меню!"})
    else:
        return JsonResponse(
            {
                "error": "Ошибка при добавлении ссылки",
                "status_code": response.status_code,
                "details": response.text,
            },
            status=500
        )


