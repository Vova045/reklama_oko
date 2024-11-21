from django.http import JsonResponse
import re
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, get_object_or_404
from .models import ProductComposition, TechnologicalOperation, MaterialsTechnologicalOperation, Nomenklatura, ParametersOfProducts, BitrixUser, AddingMaterialsTechnologicalOperation
from .models import MaterialsTechnologicalOperation, ParametersNormativesInCalculation, OperationOfTechnologicalOperation, ProductionOperation, ProductionOperationTariffs, TechnologicalLink, Folder, TechnologicalLinkComposition
from .forms import ParametersNormativesInCalculationForm
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from bitrix_calc.models import Bitrix_Goods, Bitrix_GoodsComposition
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from django.utils import timezone

import requests

from django.shortcuts import redirect

@csrf_exempt
def install(request):
    # Чтение параметров из GET и POST
    domain = request.GET.get('DOMAIN') or request.POST.get('DOMAIN')
    auth_token = request.POST.get('AUTH_ID')
    refresh_token = request.POST.get('REFRESH_ID')
    member_id = request.POST.get('member_id')
    expires_in = request.POST.get('AUTH_EXPIRES')  # Время действия токена в секундах (если доступно)

    # Проверка полученных параметров
    if not all([domain, auth_token, refresh_token, member_id]):
        return JsonResponse({
            'status': 'error',
            'message': 'Необходимые параметры не получены',
        }, status=400)

    # Расчет времени истечения токена
    expires_at = None
    if expires_in:
        try:
            expires_in = int(expires_in)
            expires_at = now() + timedelta(seconds=expires_in)
        except ValueError:
            expires_in = None

    # Сохранение или обновление записи пользователя
    bitrix_user, created = BitrixUser.objects.update_or_create(
        member_id=member_id,
        defaults={
            'domain': domain,
            'auth_token': auth_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at,
            'refresh_token_created_at': now(),
        }
    )

    # Дефолтные параметры для кнопок
    access_token = auth_token
    placements = [
        {
            'placement': 'CRM_DEAL_DETAIL_TAB',
            'handler_url': 'https://reklamaoko.ru/calculation_list',
            'title': 'Список калькуляций',
        }
    ]

    for placement_data in placements:
        placement = placement_data['placement']
        handler_url = placement_data['handler_url']
        title = placement_data['title']

        # Проверяем существующий обработчик
        check_url = f'https://{domain}/rest/placement.get/?access_token={access_token}&PLACEMENT={placement}'
        check_response = requests.get(check_url)
        check_data = check_response.json()

        if check_data.get('result'):
            # Удаляем старый обработчик
            unbind_url = f'https://{domain}/rest/placement.unbind/?access_token={access_token}&PLACEMENT={placement}'
            requests.post(unbind_url)

        # Устанавливаем новый обработчик
        bind_url = f'https://{domain}/rest/placement.bind/?access_token={access_token}&PLACEMENT={placement}&HANDLER={handler_url}&TITLE={title}'
        response = requests.post(bind_url)
        response_data = response.json()

        if not response_data.get('result'):
            return JsonResponse({
                'status': 'error',
                'message': f'Ошибка установки обработчика для {placement}: ' +
                           response_data.get('error_description', 'Неизвестная ошибка'),
            }, status=400)

    return redirect('home')


@csrf_exempt
def home(request):
    # Извлекаем список изделий
    goods = Bitrix_Goods.objects.all()

    # Извлекаем данные с группировкой для видов изделий
    compositions = (
        Bitrix_GoodsComposition.objects.values("name_type_of_goods", "type_of_goods")
        .distinct()
        .order_by("name_type_of_goods", "type_of_goods")
    )

    # Группируем данные в словарь
    grouped_compositions = {}
    for composition in compositions:
        name = composition["name_type_of_goods"]
        type_ = composition["type_of_goods"]
        if name not in grouped_compositions:
            grouped_compositions[name] = []
        grouped_compositions[name].append(type_)

    # Передаем данные в шаблон
    return render(request, "home.html", {"goods": goods, "grouped_compositions": grouped_compositions})


# Обработчик для динамической загрузки видов товаров (если используется AJAX)
@csrf_exempt
def get_item_types(request, product_id):
    if request.method == "GET":
        # Получаем связанные виды товаров для выбранного продукта
        compositions = (
            Bitrix_GoodsComposition.objects.filter(goods_id=product_id)
            .values("name_type_of_goods", "type_of_goods")
            .distinct()
            .order_by("name_type_of_goods", "type_of_goods")
        )

        # Группируем данные по name_type_of_goods
        grouped_compositions = {}
        for composition in compositions:
            name = composition["name_type_of_goods"]
            type_ = composition["type_of_goods"]
            if name not in grouped_compositions:
                grouped_compositions[name] = []
            grouped_compositions[name].append(type_)

        return JsonResponse(grouped_compositions)
    
@csrf_exempt
def filter_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        product_id = data.get("product_id")
        product_name = data.get("product_name")
        name_type_of_goods = data.get("name_type_of_goods")
        type_of_goods = data.get("type_of_goods")

        # Логика обработки полученных данных
        # Например, сохранение или фильтрация товаров

        response_data = {"status": "success", "message": "Данные успешно обработаны."}
        return JsonResponse(response_data)
        


@csrf_exempt
def calculation_preview(request):
    return render(request, 'calculation_preview.html')

@csrf_exempt
def calculation_previews(request):
    return render(request, 'calculation_previews.html')


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

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def bind_application(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)

    # Получение access_token
    access_token = request.GET.get('access_token')
    if not access_token:
        return JsonResponse({"error": "Access token is missing"}, status=400)

    # URL для добавления и проверки размещений
    BIND_URL = "https://oko.bitrix24.ru/rest/placement.bind.json"
    GET_PLACEMENTS_URL = "https://oko.bitrix24.ru/rest/placement.get.json"

    # Массив данных для размещения приложения в разных местах
    placements = [
        {"PLACEMENT": "left_menu", "TITLE": "Калькуляция", "DESCRIPTION": "Приложение для управления расчётами"},
        {"PLACEMENT": "crm.deal.list.menu", "TITLE": "Калькуляция", "DESCRIPTION": "Приложение для управления расчётами"},
        {"PLACEMENT": "crm.company.details", "TITLE": "Калькуляция", "DESCRIPTION": "Приложение для управления расчётами"},
        {"PLACEMENT": "crm.contact.details", "TITLE": "Калькуляция", "DESCRIPTION": "Приложение для управления расчётами"},
        {"PLACEMENT": "crm.activity.list.menu", "TITLE": "Калькуляция", "DESCRIPTION": "Приложение для управления расчётами"},
        {"PLACEMENT": "task.list.menu", "TITLE": "Калькуляция", "DESCRIPTION": "Приложение для управления расчётами"},
        {"PLACEMENT": "user.profile.menu", "TITLE": "Калькуляция", "DESCRIPTION": "Приложение для управления расчётами"}
    ]

    # Заголовки запроса
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Получение уже существующих размещений
    existing_placements = []
    response = requests.get(GET_PLACEMENTS_URL, headers=headers)
    if response.status_code == 200:
        existing_placements = response.json().get('result', [])
    else:
        print("Ошибка при получении текущих размещений:", response.status_code, response.text)

    # Добавление приложения в указанные места
    bind_results = []
    for placement in placements:
        # Проверка, если приложение уже добавлено в это место
        if any(p['placement'] == placement['PLACEMENT'] for p in existing_placements):
            bind_results.append({"placement": placement["PLACEMENT"], "status": "Уже добавлено"})
            continue

        # Данные для размещения
        payload = {
            "PLACEMENT": placement["PLACEMENT"],
            "HANDLER": "https://reklamaoko.ru",
            "TITLE": placement["TITLE"],
            "DESCRIPTION": placement["DESCRIPTION"]
        }

        # Запрос на добавление
        response = requests.post(BIND_URL, headers=headers, data=json.dumps(payload))
        
        # Проверка ответа
        if response.status_code == 200:
            bind_results.append({"placement": placement["PLACEMENT"], "status": "Добавлено успешно"})
        else:
            error_message = response.json().get("error_description", "Ошибка при добавлении")
            bind_results.append({
                "placement": placement["PLACEMENT"],
                "status": f"Ошибка: {response.status_code}, {error_message}"
            })
            print(f"Ошибка при добавлении {placement['PLACEMENT']}: {response.status_code}, {response.text}")

    # Ответ с результатами привязки и уже существующими размещениями
    return JsonResponse({
        "existing_placements": existing_placements,
        "bind_results": bind_results
    })

@csrf_exempt
def get_available_placements(request):
    access_token = request.GET.get('access_token')
    if not access_token:
        return JsonResponse({"error": "Access token is missing"}, status=400)

    # URL для получения списка доступных размещений
    GET_PLACEMENTS_URL = "https://oko.bitrix24.ru/rest/placement.get.json"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(GET_PLACEMENTS_URL, headers=headers)
    
    if response.status_code == 200:
        return JsonResponse({"available_placements": response.json().get('result', [])})
    else:
        return JsonResponse({
            "error": "Ошибка при получении списка доступных размещений",
            "details": response.text
        }, status=response.status_code)


def get_technological_links(request):
    product_id = request.GET.get('product_id')
    unique_links = {}
    open_all = bool(product_id)  # Флаг для открытия всех папок, если выбран product_id

    if product_id:
        product_compositions = ProductComposition.objects.filter(product_id=product_id)
        
        for product_composition in product_compositions:
            technological_link = product_composition.technology
            if technological_link:
                tech_id = technological_link.id
                tech_name = technological_link.operation_link_name
                tech_folder = technological_link.folder.name
                tech_folder_id = technological_link.folder.id
                tech_parent_id = technological_link.folder.parent.id if technological_link.folder.parent else None
                tech_parent_name = technological_link.folder.parent.name if technological_link.folder.parent else None
                
                unique_links[(tech_id, tech_name, tech_folder_id)] = {
                    'id': tech_id,
                    'name': tech_name,
                    'folder': tech_folder,
                    'folder_id': tech_folder_id,
                    'parent_id': tech_parent_id,
                    'parent_name': tech_parent_name
                }

        folder_ids = set(link['folder_id'] for link in unique_links.values())

        def add_parent_folders(folder_id):
            folder = Folder.objects.get(id=folder_id)
            if folder.parent:
                parent_id = folder.parent.id
                if parent_id not in folder_ids:
                    folder_ids.add(parent_id)
                    add_parent_folders(parent_id)

        for folder_id in folder_ids.copy():
            add_parent_folders(folder_id)
        
        filtered_folders = Folder.objects.filter(id__in=folder_ids).order_by('name')
        
        all_folders = [
            {
                'folder': folder.name,
                'folder_id': folder.id,
                'parent_id': folder.parent.id if folder.parent else None,
                'parent_name': folder.parent.name if folder.parent else None
            }
            for folder in filtered_folders
        ]
    else:
        technological_links = TechnologicalLink.objects.all()
        
        for comp in technological_links:
            tech_id = comp.id
            tech_name = comp.operation_link_name
            tech_folder = comp.folder.name
            tech_folder_id = comp.folder.id
            tech_parent_id = comp.folder.parent.id if comp.folder.parent else None
            tech_parent_name = comp.folder.parent.name if comp.folder.parent else None
            
            unique_links[(tech_id, tech_name, tech_folder_id)] = {
                'id': tech_id,
                'name': tech_name,
                'folder': tech_folder,
                'folder_id': tech_folder_id,
                'parent_id': tech_parent_id,
                'parent_name': tech_parent_name
            }
        
        all_folders = [
            {
                'folder': folder.name,
                'folder_id': folder.id,
                'parent_id': folder.parent.id if folder.parent else None,
                'parent_name': folder.parent.name if folder.parent else None
            }
            for folder in Folder.objects.filter(folder_type='Технологические узлы')
        ]

    links = list(unique_links.values())

    return JsonResponse({
        'links': links,
        'folders': all_folders,
        'open': open_all  # Передаем флаг "open"
    })


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
        # print(data)
        link_ids = data.get('links', [])  # Получаем ссылки из данных
        current_product = data.get('current_product')  # Получаем ссылки из данных

        if current_product:
            product_compositions = ProductComposition.objects.filter(
                product=current_product,
                technology__operation_link_name__in=link_ids  # Фильтруем по имени технологии
            )
            # Получаем уникальные ID тех операций, которые соответствуют фильтру
            tech_operations_ids = product_compositions.values_list('techoperation', flat=True).distinct()
            if tech_operations_ids:
                operations = TechnologicalOperation.objects.filter(
                    id__in=tech_operations_ids,
                ).distinct()
            else:
                operations = []  # Если операций нет, возвращаем пустой список
        else:
            if link_ids and link_ids[0]: 
                link = TechnologicalLink.objects.filter(
                    operation_link_name__in=link_ids
                )
                operations = TechnologicalOperation.objects.filter(
                    technologicallinkcomposition__technical_link__id__in=link
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
            # else:
            #     y = TechnologicalOperation.objects.filter(
            #         operation_link_name=x
            #     )
            # print(y)
        #     product_compositions = ProductComposition.objects.filter(
        #     operation__in=y # Фильтруем по выбранным операциям
        # )[0]
            operation_list.append({
                'id': ol['id'],
                'name': ol['name'],  # Предполагаем, что есть поле name у TechnologicalOperation
                'formula': ol['formula'],  # Предполагаем, что есть поле formula у TechnologicalOperation
                'link': x
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
        print('иннер_операйшен')
        print(inner_operations)
        return JsonResponse({'operations': operation_list, 'inner_operations': inner_operations })

def update_selected_operations(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_operations = data.get('selected_operations')
        # print(selected_operations)
        if selected_operations and selected_operations[0]: 
            return JsonResponse({'success': True, 'selected_operations': selected_operations})
        else:
            return JsonResponse({'success': False, 'message': 'Выделенных операций нет.'})

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса.'})
def update_selected_nomenclature(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_nomenclature = data.get('selected_nomenclature')
        # print(selected_nomenclature)  # Выводим выделенные номенклатуры в консоль для проверки

        if selected_nomenclature and selected_nomenclature[0]:
            return JsonResponse({'success': True, 'selected_nomenclature': selected_nomenclature})
        else:
            return JsonResponse({'success': False, 'message': 'Выделенных номенклатур нет.'})

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса.'})

from django.db.models import Q  # Импортируем Q для составления сложных запросов

def get_nomenclature(request):
    # Получаем список выбранных операций
    operations_ids = request.GET.get('operations', '')
    operations_ids_list = operations_ids.split(',') if operations_ids else []
    
    # Получаем id выбранного продукта
    product_id = request.GET.get('product', '')
    
    if operations_ids_list and product_id:
        # Находим все ProductComposition, которые соответствуют выбранному продукту
        product_compositions = ProductComposition.objects.filter(
            product_id=product_id,
            techoperation__in=operations_ids_list  # Отфильтровываем по выбранным операциям
        )
        
        # Собираем все уникальные (nomenklatura, technicological_operation) из найденных ProductComposition
        nomenclature_and_operations = product_compositions.values_list(
            'nomenclature', 'techoperation'
        ).distinct()

        # Находим все записи в MaterialsTechnologicalOperation, у которых совпадают nomenklatura и techoperation
        nomenclature_of_techoperations = MaterialsTechnologicalOperation.objects.filter(
            Q(nomenklatura__in=[n[0] for n in nomenclature_and_operations]) &
            Q(technicological_operation__in=[n[1] for n in nomenclature_and_operations])
        ).distinct()
    else:
        nomenclature_of_techoperations = []

    # Формируем список для возвращаемого ответа
    nomenclature_list = [{
        'id': item.id,
        'name': str(item.nomenklatura), 
        'technicological_operation': str(item.technicological_operation)
    } for item in nomenclature_of_techoperations]
    print(nomenclature_list)
    return JsonResponse({'nomenclature': nomenclature_list})


def extract_variables(formula):
    # print(formula)
    return re.findall(r'\b\w+\b', formula)
def get_all_parameters_without_formula(variable_names):
    variables_without_formula = set() 
    next_variables_to_check = set(variable_names)  
    while next_variables_to_check: 
        current_variable = next_variables_to_check.pop()
        parameter = ParametersOfProducts.objects.filter(formula_name=current_variable).first()
        if parameter and parameter.formula:
            new_variables = extract_variables(parameter.formula)
            # print(new_variables)
            next_variables_to_check.update(new_variables) 
        else:
            variables_without_formula.add(current_variable)

    return variables_without_formula

def get_parameters_product_bitrix(request):
    print('get_parameters_product_bitrix')

    # Получаем id и имя товара для поиска
    goods_id = request.GET.get('goods_id')
    bitrix_goods_name = request.GET.get('bitrix_goods_name')

    # Получаем типы товаров и их родителей (параметр передается как строка JSON)
    selected_types_json = request.GET.get('selected_types', '[]')  # Если параметр отсутствует, по умолчанию пустой список

    try:
        # Преобразуем строку JSON в Python объект (список словарей)
        selected_types = json.loads(selected_types_json)
    except json.JSONDecodeError:
        selected_types = []

    # Логирование для отладки
    print(f"goods_id: {goods_id}")
    print(f"bitrix_goods_name: {bitrix_goods_name}")
    print(f"selected_types: {selected_types}")

    # Здесь можно добавить вашу логику для обработки полученных типов
    # Например, возвращать параметры для каждого типа товара

    if goods_id and bitrix_goods_name:
        # Ищем объект Bitrix_Goods по id и bitrix_goods_name
        bitrix_goods = Bitrix_Goods.objects.filter(id=goods_id, bitrix_goods_name=bitrix_goods_name).first()
        if not bitrix_goods:
            return JsonResponse({'error': 'Товар не найден'}, status=404)
        
        if selected_types:
            operations = []  # List to store all TechnologicalOperation objects
            for selected_type in selected_types:                
                # Filter the Bitrix_GoodsComposition objects based on the selected type
                bitrix_goods_composition = Bitrix_GoodsComposition.objects.filter(
                    goods=bitrix_goods, 
                    name_type_of_goods=selected_type['parent'], 
                    type_of_goods=selected_type['type']
                )
                
                if not bitrix_goods_composition.exists():
                    return JsonResponse({'error': 'Состав товара не найден'}, status=404)
                
                
                # Iterate over the filtered Bitrix_GoodsComposition objects and get the techoperation
                for composition in bitrix_goods_composition:
                    tech_operation = composition.techoperation
                    if not tech_operation:
                        return JsonResponse({'error': 'Технологическая операция не найдена'}, status=404)
                    
                    # Append the tech_operation to the operations list
                    operations.append(tech_operation)


        all_parameters = {}
        
        for operation in operations:
            if operation.formula:
                initial_variables = extract_variables(operation.formula)
                variables_without_formula = get_all_parameters_without_formula(initial_variables)
                matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                for item in matching_parameters:
                    if item.parameters_product not in all_parameters:
                        all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
            
            # Аналогичные действия для других типов операций
            operation_of_tech_ops = OperationOfTechnologicalOperation.objects.filter(technicological_operation=operation)
            for op_tech_op in operation_of_tech_ops:
                if op_tech_op.formula:
                    initial_variables = extract_variables(op_tech_op.formula)
                    variables_without_formula = get_all_parameters_without_formula(initial_variables)
                    matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                    for item in matching_parameters:
                        if item.parameters_product not in all_parameters:
                            all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
            
            material_of_tech_ops = MaterialsTechnologicalOperation.objects.filter(technicological_operation=operation)
            for material_tech_op in material_of_tech_ops:
                if material_tech_op.formula:
                    initial_variables = extract_variables(material_tech_op.formula)
                    variables_without_formula = get_all_parameters_without_formula(initial_variables)
                    matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                    for item in matching_parameters:
                        if item.parameters_product not in all_parameters:
                            all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
            
            addmaterial_of_tech_ops = AddingMaterialsTechnologicalOperation.objects.filter(technicological_operation=operation)
            for addmaterial_tech_op in addmaterial_of_tech_ops:
                if addmaterial_tech_op.formula:
                    initial_variables = extract_variables(addmaterial_tech_op.formula)
                    variables_without_formula = get_all_parameters_without_formula(initial_variables)
                    matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                    for item in matching_parameters:
                        if item.parameters_product not in all_parameters:
                            all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
        print(list(all_parameters.values()))
        # Возвращаем параметры в виде JSON
        return JsonResponse({'parameters': list(all_parameters.values())})
    else:
        return JsonResponse({'error': 'Параметры товара не переданы'}, status=400)
    
def get_parameters_product(request):
    print('get_parameters_product')
    operations_ids = request.GET.get('operations', '')
    print(operations_ids)
    operations_ids = operations_ids.split(',') if operations_ids else []
    
    if operations_ids:
        operations = TechnologicalOperation.objects.filter(operation_link_name__in=operations_ids)
        
        all_parameters = {}
        
        for operation in operations:
            if operation.formula:
                initial_variables = extract_variables(operation.formula)
                variables_without_formula = get_all_parameters_without_formula(initial_variables)
                matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                for item in matching_parameters:
                    if item.parameters_product not in all_parameters:
                        all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
            operation_of_tech_ops = OperationOfTechnologicalOperation.objects.filter(technicological_operation=operation)
            for op_tech_op in operation_of_tech_ops:
                if op_tech_op.formula:
                    initial_variables = extract_variables(op_tech_op.formula)
                    variables_without_formula = get_all_parameters_without_formula(initial_variables)
                    matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                    for item in matching_parameters:
                        if item.parameters_product not in all_parameters:
                            all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
            material_of_tech_ops = MaterialsTechnologicalOperation.objects.filter(technicological_operation=operation)
            for material_tech_op in material_of_tech_ops:
                if material_tech_op.formula:
                    initial_variables = extract_variables(material_tech_op.formula)
                    variables_without_formula = get_all_parameters_without_formula(initial_variables)
                    matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                    for item in matching_parameters:
                        if item.parameters_product not in all_parameters:
                            all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
            addmaterial_of_tech_ops = AddingMaterialsTechnologicalOperation.objects.filter(technicological_operation=operation)
            for addmaterial_tech_op in addmaterial_of_tech_ops:
                if addmaterial_tech_op.formula:
                    initial_variables = extract_variables(addmaterial_tech_op.formula)
                    variables_without_formula = get_all_parameters_without_formula(initial_variables)
                    matching_parameters = ParametersOfProducts.objects.filter(formula_name__in=variables_without_formula)
                    for item in matching_parameters:
                        if item.parameters_product not in all_parameters:
                            all_parameters[item.parameters_product] = {'id': item.id, 'name': item.parameters_product}
        print(list(all_parameters.values()))
        print('конец')
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
    print('update_parameters_product')

    if request.method == 'POST':
        try:
            def replace_formula_with_calculation(tech_operation):
                final_formula = tech_operation.formula  # Получаем исходную формулу операции
                # print(final_formula)
                while True:
                    initial_formula = final_formula  # Сохраняем текущую формулу для проверки изменений
                    
                    elements = final_formula.split()  # Разделяем формулу на отдельные элементы
                    # print(initial_formula)
                    # Перебираем все элементы формулы
                    for i, element in enumerate(elements):
                        # print(i,element)
                        try:
                            # print(i)
                            # print(element)
                            # Ищем, является ли элемент представлением
                            param_obj = ParametersOfProducts.objects.filter(Q(formula_name=element)).first()
                            # print(param_obj)

                            # Проверяем, что param_obj найден и содержит формулу
                            if param_obj and param_obj.formula:
                                # Если у представления есть формула расчета, заменяем его на формулу с учетом скобок
                                elements[i] = f" ( {param_obj.formula} ) "
                        except ParametersOfProducts.DoesNotExist:
                            # Если представление не найдено, продолжаем
                            pass
                    # print(final_formula)
                    # Соединяем все элементы обратно в строку
                    final_formula = ' '.join(elements)
                    # print(final_formula)
                    # Если формула не изменилась, выходим из цикла
                    if final_formula == initial_formula:
                        break
                # Обновляем значение formula у технологической операции
                tech_operation.formula = final_formula
                # print(tech_operation.formula)

            # Загружаем JSON данные из запроса
            data = json.loads(request.body)
            product_parameters = data.get('product_parameters', {})
            inner_operations = data.get('inner_operations', {})
            nomenclature_list = data.get('nomenclature_list')
            # print(nomenclature_list)
            technological_operations = data.get('technological_operations', [])
            technological_operation_list = TechnologicalOperation.objects.filter(operation_link_name__in=technological_operations)
            price_cost_with_adds = 0
            final_prices = 0


            def replace_min(tokens):
                i = 0
                while i < len(tokens):
                    # Ищем "Мин" и проверяем, что есть достаточно элементов после него
                    if tokens[i] == 'Мин' and i + 4 < len(tokens) and tokens[i+1] == '(' and tokens[i+3] == ',' and tokens[i+5] == ')':
                        # Извлекаем два числа после "Мин"
                        num1 = tokens[i+2]
                        num2 = tokens[i+4]
                        
                        # Находим меньшее из двух чисел или первое, если они равны
                        min_value = num1 if num1 <= num2 else num2
                        
                        # Заменяем 'Мин', '(', num1, ',', num2, ')' на min_value
                        tokens = tokens[:i] + [min_value] + tokens[i+6:]  
                    else:
                        i += 1  # Переходим к следующему элементу
                return tokens
                            
            operations_prices = []
            operations_fullprices = []
            for techlink in technological_operation_list:
                final_price_current_techoperation = 0
                # print(techlink.operation_link_name)
                # nomenclature_count = len(nomenclature_list) if nomenclature_list is not None else 0
                # Перебираем каждый параметр, чтобы сохранить или обновить его
                parameters_dict = {}
                for param_name, param_value in product_parameters.items():
                    
                    parameter = ParametersOfProducts.objects.get(parameters_product=param_name)
                    parameters_dict[parameter.formula_name] = param_value
                    # print(parameters_dict)
                total_inner_operations_sum = 0
                for inner_name in inner_operations:
                    # print('Операции')
                    # print(inner_name)
                    inner_operation = ProductionOperation.objects.filter(operation_name=inner_name).first()
                    inner_operations = ProductionOperation.objects.filter(operation_name=inner_name)
                    tarif = ProductionOperationTariffs.objects.filter(production_operation=inner_operation).first()
                    inner_operation2 = OperationOfTechnologicalOperation.objects.filter(
                        production_operation=inner_operation,
                        technicological_operation=techlink)
                    for inner in inner_operation2:
                        # print(inner)
                        replace_formula_with_calculation(inner)
                        tokens = inner.formula.replace('*', ' * ').replace('/', ' / ').split()
                        cleaned_tokens = []
                        # print(tokens)
                        for i in range(len(tokens)):
                            if tokens[i] in parameters_dict:
                                tokens[i] = parameters_dict[tokens[i]]
                        
                        # Присваиваем результат выполнения функции обратно в tokens
                        tokens = replace_min(tokens)
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
                        # print(result)

                        # print(result)
                        def safe_float(value):
                            try:
                                return float(value)
                            except (ValueError, TypeError):
                                return 0.0  # Возвращаем 0.0 в случае ошибки

                        # Используем безопасное преобразование
                        lead_time = safe_float(tarif.lead_time)
                        # print(lead_time)
                        preporation_time = safe_float(tarif.preporation_time)
                        # print(preporation_time)
                        min_time = safe_float(tarif.min_time)
                        # print(min_time)
                        many_people = safe_float(tarif.many_people)
                        # print(many_people)
                        salary = safe_float(inner_operation.job_title.salary)
                        # print(salary)

                        result_to_done = preporation_time + lead_time * result
                        # print(result_to_done)
                        # Проверяем условие и вычисляем result2
                        if result_to_done < min_time:
                            result2 = ((min_time * many_people) / 60) * salary
                        else:
                            result2 = (result_to_done * many_people / 60) * salary
                        # Умножаем на количество номенклатуры
                        # result2 = result2 * nomenclature_count
                        print(f"{inner} -- Результат операции: {result2}")
                        total_inner_operations_sum += result2

                total_nomenclature_sum = 0

                for nomenclature in nomenclature_list:
                    # print('Материал')
                    # print(nomenclature)
                    # Получаем строковое значение для сравнения, если techlink является объектом
                    # Проверка совпадения с использованием strip() для строк
                    if techlink.operation_link_name == nomenclature['operation']:
                        nomenclature_name = nomenclature['nomenclature']
                        # print(nomenclature_name)
                        material_operations = MaterialsTechnologicalOperation.objects.filter(
                            nomenklatura__nomenklatura_name=nomenclature_name,
                            technicological_operation=techlink
                        )
                        
                        for material in material_operations:
                            # print(material.nomenklatura)
                            if material.formula is None:
                                material.formula = techlink.formula
                            # print(material.formula)
                            replace_formula_with_calculation(material)
                            
                            # Обработка формулы
                            tokens = material.formula.replace('*', ' * ').replace('/', ' / ').split()
                            cleaned_tokens = [
                                str(parameters_dict.get(token, token)) if token in parameters_dict else token
                                for token in tokens
                            ]

                            final_formula = ' '.join(cleaned_tokens)
                            result = eval(final_formula)

                            # Дополнительные вычисления
                            default_parameters = ParametersNormativesInCalculation._meta.get_field('overheads').default
                            salary_fund_default = ParametersNormativesInCalculation._meta.get_field('salary_fund').default
                            profit_default = ParametersNormativesInCalculation._meta.get_field('profit').default
                            payroll_default = ParametersNormativesInCalculation._meta.get_field('payroll').default

                            matched_nomenklaturas = []

                            if material.nomenklatura and material.nomenklatura.nomenklatura_name in nomenclature_list:
                                matched_nomenklaturas.append(material.nomenklatura)
                            
                            nomenclature = material.nomenklatura

                                                        # Суммирование цен номенклатур
                            # Присваиваем 1, если значение отсутствует или является пустой строкой
                            if not nomenclature.price:
                                nomenclature.price = 1
                            if not nomenclature.waste_rate:
                                nomenclature.waste_rate = 1
                            if not nomenclature.material_markup:
                                nomenclature.material_markup = 1

                            # Преобразуем значения в float для последующего использования
                            nomenclature.price = float(nomenclature.price)
                            nomenclature.waste_rate = float(nomenclature.waste_rate)
                            nomenclature.material_markup = float(nomenclature.material_markup)
                            nomenclature_total = nomenclature.price * nomenclature.waste_rate * nomenclature.material_markup
                            # nomenclature_price_without_percent_total = sum(
                            #     float(nomenclature.price) for nomenclature in matched_nomenklaturas
                            # )
                            result = nomenclature_total * result
                            # print(result2)
                            # print(f"{material} -- Результат номенклатуры: {result}")
                            total_nomenclature_sum += result

                technological_operation = TechnologicalOperation.objects.filter(operation_link_name=techlink).first()

                    # Получаем все связанные объекты AddingMaterialsTechnologicalOperation
                adding_materials_operations = AddingMaterialsTechnologicalOperation.objects.filter(technicological_operation=technological_operation)
                
                # Проходимся по всем найденным объектам и выводим их
                total_adding_material_sum = 0
                for adding_material in adding_materials_operations:
                    # print('Добавочные материалы')
                    # Сохраняем объект Nomenklatura в переменную
                    nomenklatura_price = adding_material.nomenklatura.price
                    # print(nomenklatura_price)
                    if adding_material.formula is None:
                        adding_material.formula = techlink.formula
                        # print(adding_material.formula)
                    # print(adding_material.formula)
                    replace_formula_with_calculation(adding_material)
                    # print(adding_material.formula)
                    # Обработка формулы
                    tokens = adding_material.formula.replace('*', ' * ').replace('/', ' / ').split()
                    # print(tokens)
                    cleaned_tokens = [
                        str(parameters_dict.get(token, token)) if token in parameters_dict else token
                        for token in tokens
                    ]
                    
                    final_formula = ' '.join(cleaned_tokens)
                    # print(final_formula)
                    result = eval(final_formula)
                    # print(result)


                    matched_nomenklaturas = []

                    if adding_material.nomenklatura and adding_material.nomenklatura.nomenklatura_name in nomenclature_list:
                        matched_nomenklaturas.append(adding_material.nomenklatura)
                    nomenclature = adding_material.nomenklatura
                    # Суммирование цен номенклатур
                    if not nomenclature.price:
                        nomenclature.price = 1
                    if not nomenclature.waste_rate:
                        nomenclature.waste_rate = 1
                    if not nomenclature.material_markup:
                        nomenclature.material_markup = 1

                    # Преобразуем значения в float для последующего использования
                    nomenclature.price = float(nomenclature.price)
                    nomenclature.waste_rate = float(nomenclature.waste_rate)
                    nomenclature.material_markup = float(nomenclature.material_markup)
                    nomenclature_total = nomenclature.price * nomenclature.waste_rate * nomenclature.material_markup

                    # nomenclature_price_without_percent_total = sum(
                    #     float(nomenclature.price) for nomenclature in matched_nomenklaturas
                    # )
                    result = nomenclature_total * result
                    result2 = (
                        result +
                        result * salary_fund_default / 100 +
                        result * profit_default / 100
                    )
                    
                    # print(f"{adding_material} -- Результат номенклатуры: {result2}")
                    total_adding_material_sum += result2
                # Теперь добавить AddMaterials и потом всё соединить
                total_sum_operations = total_inner_operations_sum 
                total_sum_materials = total_adding_material_sum + total_nomenclature_sum 
                # print(total_sum_operations)
                # print(total_sum_materials)

                overheads_default = ParametersNormativesInCalculation._meta.get_field('overheads').default
                salary_fund_default = ParametersNormativesInCalculation._meta.get_field('salary_fund').default
                profit_default = ParametersNormativesInCalculation._meta.get_field('profit').default
                payroll_default = ParametersNormativesInCalculation._meta.get_field('payroll').default

                price_material = total_nomenclature_sum
                print(f"Материалы: {price_material}")
                price_add_material = total_adding_material_sum
                print(f"Дополнительные Материалы: {price_add_material}")
                price_salary = total_sum_operations
                print(f"Заработная плата: {price_salary}")
                price_payroll = total_sum_operations * payroll_default / 100
                print(f"Отчисления на зарплату: {price_payroll}")
                price_overheads = total_sum_operations * overheads_default / 100
                print(f"Накладные расходы: {price_overheads}")
                price_cost = price_material + price_salary + price_overheads + price_payroll
                price_cost_with_add = price_cost + price_add_material

                print(f"Себестоимость: {price_cost}")
                price_profit = price_cost_with_add * profit_default / 100
                print(f"Прибыль: {price_profit}")
                price_salary_fund = price_cost_with_add * salary_fund_default / 100
                print(f"Зарплатный фонд: {price_salary_fund}")
                final_price = price_cost_with_add + price_profit + price_salary_fund
                print(f"Цена: {final_price}")
                price_cost_with_adds += price_cost_with_add
                # final_prices += final_price
                final_price_current_techoperation += final_price
                operations_prices.append({
                    'operation': techlink.operation_link_name,
                    'final_price': final_price_current_techoperation
                })
                operations_fullprices.append({
                    'operation': techlink.operation_link_name,
                    'price_material': price_material,
                    'price_add_material':price_add_material,
                    'price_salary':price_salary,
                    'price_payroll':price_payroll,
                    'price_overheads':price_overheads,
                    'price_cost':price_cost,
                    'price_profit':price_profit,
                    'price_salary_fund':price_salary_fund,
                    'price_cost_with_add':price_cost_with_add,
                    'final_price':final_price_current_techoperation
                })


            all_final_prices = sum(item['final_price'] for item in operations_prices)
            all_price_material = sum(item['price_material'] for item in operations_fullprices)
            print(f"Общие Материалы: {all_price_material}")

            all_price_add_material = sum(item['price_add_material'] for item in operations_fullprices)
            print(f"Общие Дополнительные материалы: {all_price_add_material}")

            all_price_salary = sum(item['price_salary'] for item in operations_fullprices)
            print(f"Общие Заработная плата: {all_price_salary}")

            all_price_payroll = sum(item['price_payroll'] for item in operations_fullprices)
            print(f"Общие Отчисления на зарплату: {all_price_payroll}")

            all_price_overheads = sum(item['price_overheads'] for item in operations_fullprices)
            print(f"Общие Накладные расходы: {all_price_overheads}")

            all_price_cost = sum(item['price_cost'] for item in operations_fullprices)
            print(f"Общая Себестоимость: {all_price_cost}")

            all_price_profit = sum(item['price_profit'] for item in operations_fullprices)
            print(f"Общая Прибыль: {all_price_profit}")

            all_price_salary_fund = sum(item['price_salary_fund'] for item in operations_fullprices)
            print(f"Общий Зарплатный фонд: {all_price_salary_fund}")

            all_price_cost_with_add = sum(item['price_cost_with_add'] for item in operations_fullprices)
            print(f"Общая Себестоимость с дополнительными материалами: {all_price_cost_with_add}")

            all_final_price = sum(item['final_price'] for item in operations_fullprices)
            print(f"Общая Итоговая цена: {all_final_price}")
            # all_final_prices += final_price_current_techoperation
            price_cost_with_adds += price_cost_with_adds
            default_parameters = ParametersNormativesInCalculation._meta.get_field('overheads').default
            salary_fund_default = ParametersNormativesInCalculation._meta.get_field('salary_fund').default
            profit_default = ParametersNormativesInCalculation._meta.get_field('profit').default
            payroll_default = ParametersNormativesInCalculation._meta.get_field('payroll').default

            # print(operations_prices)
            response_data = {
                'success': True,
                'total_nomenclature': price_cost_with_adds,
                'total_final_price': all_final_prices,
                'operations': operations_prices,
                'default_parameters': {
                    'overheads': default_parameters,
                    'salary_fund': salary_fund_default,
                    'profit': profit_default,
                    'payroll': payroll_default
                }
            }
            # print(response_data)
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

        # Добавляем пустую опцию для родительской папки
        folder_map[None] = {
            'id': None,
            'name': 'Без родительской папки',
            'parent_id': None,
            'children': [],
            'parent_name': None
        }

        # Заполняем словарь данными о папках
        for folder in matching_folders:
            folder_map[folder.id] = {
                'id': folder.id,
                'name': folder.name,
                'parent_id': folder.parent_id,
                'children': [],
                'parent_name': folder.parent.name if folder.parent else None
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
        folders = Folder.objects.all().select_related('parent')
        folder_map = {}

        # Добавляем пустую опцию для родительской папки
        folder_map[None] = {
            'id': None,
            'name': 'Без родительской папки',
            'parent': None,
            'children': []
        }

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

from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import BitrixUser

import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
from .models import BitrixUser

import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
from .models import BitrixUser

from datetime import timedelta
from django.utils.timezone import now

def update_tokens(request):
    """
    Обновляет токены пользователя в базе данных.
    """
    # Получение параметров из POST-запроса
    member_id = request.POST.get('member_id')
    domain = request.POST.get('DOMAIN')
    auth_token = request.POST.get('AUTH_ID')
    refresh_token = request.POST.get('REFRESH_ID')
    expires_in = request.POST.get('AUTH_EXPIRES')  # Время действия токена в секундах (опционально)

    # Проверка необходимых параметров
    if not all([member_id, domain, auth_token, refresh_token]):
        return JsonResponse({
            'status': 'error',
            'message': 'Необходимые параметры не переданы.'
        }, status=400)

    # Расчет времени истечения токена (если предоставлено)
    expires_at = None
    if expires_in:
        try:
            expires_in = int(expires_in)
            expires_at = now() + timedelta(seconds=expires_in)
        except ValueError:
            expires_at = None  # Игнорируем, если значение неверное

    # Обновление или создание записи пользователя
    bitrix_user, _ = BitrixUser.objects.update_or_create(
        member_id=member_id,
        defaults={
            'domain': domain,
            'auth_token': auth_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at,
            'refresh_token_created_at': now(),
        }
    )

    # Возвращение успешного ответа
    return JsonResponse({
        'status': 'success',
        'message': 'Токены успешно обновлены.',
        'bitrix_user': {
            'member_id': bitrix_user.member_id,
            'domain': bitrix_user.domain,
            'auth_token': bitrix_user.auth_token,
            'expires_at': bitrix_user.expires_at,
            'refresh_token_created_at': bitrix_user.refresh_token_created_at,
        }
    })


def get_nomenklatura_by_folder(request, folder_id):
    # Получаем все номенклатуры, которые относятся к выбранной папке
    nomenklaturas = Nomenklatura.objects.filter(folder_id=folder_id).values('id', 'nomenklatura_name')
    data = [{'id': n['id'], 'name': n['nomenklatura_name']} for n in nomenklaturas]
    return JsonResponse(data, safe=False)
    
def get_technical_operations_by_folder(request, folder_id):
    operations = TechnologicalOperation.objects.filter(folder_id=folder_id).values('id', 'operation_link_name')
    data = [{'id': op['id'], 'name': op['operation_link_name']} for op in operations]
    return JsonResponse(data, safe=False)


def get_production_operation_by_folder(request, folder_id):
    production_operations = ProductionOperation.objects.filter(folder_id=folder_id).values('id', 'operation_name')
    data = [{'id': op['id'], 'name': op['operation_name']} for op in production_operations]
    return JsonResponse(data, safe=False)

def get_add_nomenklature_by_folder(request, folder_id):
    # Получаем все номенклатуры, которые относятся к выбранной папке
    nomenklaturas = Nomenklatura.objects.filter(folder_id=folder_id).values('id', 'nomenklatura_name')
    data = [{'id': n['id'], 'name': n['nomenklatura_name']} for n in nomenklaturas]
    return JsonResponse(data, safe=False)


def get_filtered_fields(request):
    folder_id = request.GET.get('folder_id')  # Получаем ID папки
    field_name = request.GET.get('field_name')  # Получаем имя поля для фильтрации
    if not folder_id or not field_name:
        return JsonResponse({'error': 'Missing folder_id or field_name'}, status=400)
    folder = Folder.objects.get(id=folder_id)
    if field_name == 'technology':
        options = TechnologicalLink.objects.filter(folder=folder).values('id', 'operation_link_name')
    else:
        return JsonResponse({'error': 'Invalid field_name'}, status=400)
    # Формируем список опций
    options_list = list(options)
    return JsonResponse({'options': options_list})

def get_technology_of_product(request):
    technology_id = request.GET.get('technology_id')
    
    # Проверяем, что ID узла был передан
    if not technology_id:
        return JsonResponse({'error': 'Missing technology_id'}, status=400)

    try:
        # Получаем объект технологического узла по ID
        technology = TechnologicalLink.objects.get(id=technology_id)
        
        # Находим все технологические операции, связанные с данным узлом
        operations = TechnologicalLinkComposition.objects.filter(technical_link=technology).select_related('technical_operation')
        
        # Формируем список операций с нужными полями
        operations_data = [
            {
                'id': operation.technical_operation.id,
                'operation_link_name': operation.technical_operation.operation_link_name,
            }
            for operation in operations
        ]

        # Возвращаем данные
        return JsonResponse({'operations': operations_data})

    except TechnologicalLink.DoesNotExist:
        return JsonResponse({'error': 'Technology not found'}, status=404)
def get_technology_of_goods(request):
    technology_id = request.GET.get('technology_id')
    
    # Проверяем, что ID узла был передан
    if not technology_id:
        return JsonResponse({'error': 'Missing technology_id'}, status=400)

    try:
        # Получаем объект технологического узла по ID
        technology = TechnologicalLink.objects.get(id=technology_id)
        
        # Находим все технологические операции, связанные с данным узлом
        operations = TechnologicalLinkComposition.objects.filter(technical_link=technology).select_related('technical_operation')
        
        # Формируем список операций с нужными полями
        operations_data = [
            {
                'id': operation.technical_operation.id,
                'operation_link_name': operation.technical_operation.operation_link_name,
            }
            for operation in operations
        ]

        # Возвращаем данные
        return JsonResponse({'operations': operations_data})

    except TechnologicalLink.DoesNotExist:
        return JsonResponse({'error': 'Technology not found'}, status=404)
    

def get_nomenclature_by_techoperation(request):
    tech_operation_id = request.GET.get('tech_operation_id')
    if not tech_operation_id:
        return JsonResponse({'error': 'Missing tech_operation_id'}, status=400)
    
    # Находим все записи в MaterialsTechnologicalOperation, связанные с этой технологической операцией
    materials_operations = MaterialsTechnologicalOperation.objects.filter(technicological_operation_id=tech_operation_id)

    # Собираем номенклатуру, связанную с каждой найденной записью
    nomenclature_options = []
    for item in materials_operations:
        nomenclature = item.nomenklatura
        if nomenclature:
            nomenclature_options.append({
                'id': nomenclature.id,
                'nomenklatura_name': nomenclature.nomenklatura_name,
            })

    return JsonResponse({'options': nomenclature_options})


def get_folder_name_by_technology(request):
    technology_id = request.GET.get('technology_id')
    print(technology_id)
    if not technology_id:
        return JsonResponse({'error': 'Missing technology_id'}, status=400)

    try:
        # Получаем объект технологического узла
        technology = TechnologicalLink.objects.get(id=technology_id)
        print(technology)
        folder = Folder.objects.filter(folder_type='Технологические узлы').get(id=technology.folder.id)
        print(folder.name)
        print(folder.id)

        # Получаем имя папки, связанной с этим узлом
        # folder_name = technology.folder.name if technology.folder else None
        return JsonResponse({'folder_name': folder.name, 'folder_id': folder.id})

    except TechnologicalLink.DoesNotExist:
        return JsonResponse({'error': 'Technology not found'}, status=404)
    



@csrf_exempt
def update_parameters_product_bitrix(request):
    print('update_parameters_product')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_types = data.get('selectedTypes', [])
            selected_product_id = data.get('selectedProductId')
            bitrix_goods = Bitrix_Goods.objects.filter(id=selected_product_id).first()
            if not bitrix_goods:
                return JsonResponse({'error': 'Товар не найден'}, status=404)
            def replace_formula_with_calculation(tech_operation):
                final_formula = tech_operation.formula  # Получаем исходную формулу операции
                # print(final_formula)
                while True:
                    initial_formula = final_formula  # Сохраняем текущую формулу для проверки изменений
                    
                    elements = final_formula.split()  # Разделяем формулу на отдельные элементы
                    # print(initial_formula)
                    # Перебираем все элементы формулы
                    for i, element in enumerate(elements):
                        # print(i,element)
                        try:
                            # print(i)
                            # print(element)
                            # Ищем, является ли элемент представлением
                            param_obj = ParametersOfProducts.objects.filter(Q(formula_name=element)).first()
                            # print(param_obj)

                            # Проверяем, что param_obj найден и содержит формулу
                            if param_obj and param_obj.formula:
                                # Если у представления есть формула расчета, заменяем его на формулу с учетом скобок
                                elements[i] = f" ( {param_obj.formula} ) "
                        except ParametersOfProducts.DoesNotExist:
                            # Если представление не найдено, продолжаем
                            pass
                    # print(final_formula)
                    # Соединяем все элементы обратно в строку
                    final_formula = ' '.join(elements)
                    # print(final_formula)
                    # Если формула не изменилась, выходим из цикла
                    if final_formula == initial_formula:
                        break
                # Обновляем значение formula у технологической операции
                tech_operation.formula = final_formula
                # print(tech_operation.formula)
            if selected_types:
                nomenclature_list = []  # List to store all TechnologicalOperation objects
                inner_operations = []  # List to store all TechnologicalOperation objects
                operations = []  # List to store all TechnologicalOperation objects
                compositions = []
                for selected_type in selected_types:                
                    # Filter the Bitrix_GoodsComposition objects based on the selected type
                    bitrix_goods_composition = Bitrix_GoodsComposition.objects.filter(
                        goods=bitrix_goods, 
                        name_type_of_goods=selected_type['parent'], 
                        type_of_goods=selected_type['type']
                    )
                    if not bitrix_goods_composition.exists():
                        return JsonResponse({'error': 'Состав товара не найден'}, status=404)
                    for composition in bitrix_goods_composition:
                        tech_operation = composition.techoperation
                        nomenclature_in = composition.nomenclature
                        inner_operations_of = OperationOfTechnologicalOperation.objects.filter(technicological_operation = tech_operation)
                        for inner in inner_operations_of:
                            inner_operation_in = inner.production_operation
                            print(inner_operation_in)
                        
                        if not tech_operation:
                            return JsonResponse({'error': 'Технологическая операция не найдена'}, status=404)

                        operations.append(tech_operation)
                        nomenclature_list.append(nomenclature_in)
                        inner_operations.append(inner_operation_in)
                        compositions.append({
                            'composition': composition,
                            'operations': tech_operation,
                            'nomenclature': nomenclature_in,
                            'inner_operations': inner_operation_in,
                        })
                        
            product_parameters = data.get('product_parameters', {})
            technological_operation_list = operations
            price_cost_with_adds = 0
            final_prices = 0
            def replace_min(tokens):
                i = 0
                while i < len(tokens):
                    # Ищем "Мин" и проверяем, что есть достаточно элементов после него
                    if tokens[i] == 'Мин' and i + 4 < len(tokens) and tokens[i+1] == '(' and tokens[i+3] == ',' and tokens[i+5] == ')':
                        # Извлекаем два числа после "Мин"
                        num1 = tokens[i+2]
                        num2 = tokens[i+4]
                        
                        # Находим меньшее из двух чисел или первое, если они равны
                        min_value = num1 if num1 <= num2 else num2
                        
                        # Заменяем 'Мин', '(', num1, ',', num2, ')' на min_value
                        tokens = tokens[:i] + [min_value] + tokens[i+6:]  
                    else:
                        i += 1  # Переходим к следующему элементу
                return tokens
            operations_prices = []
            operations_fullprices = []
            for techlink in technological_operation_list:
                print(techlink)
                final_price_current_techoperation = 0
                parameters_dict = {}
                for param_name, param_value in product_parameters.items():
                    parameter = ParametersOfProducts.objects.get(parameters_product=param_name)
                    parameters_dict[parameter.formula_name] = param_value
                total_inner_operations_sum = 0
                for inner_name in inner_operations:
                    inner_operation = ProductionOperation.objects.filter(operation_name=inner_name).first()
                    inner_operations = ProductionOperation.objects.filter(operation_name=inner_name)
                    tarif = ProductionOperationTariffs.objects.filter(production_operation=inner_operation).first()
                    inner_operation2 = OperationOfTechnologicalOperation.objects.filter(
                        production_operation=inner_operation,
                        technicological_operation=techlink)
                    for inner in inner_operation2:
                        replace_formula_with_calculation(inner)
                        tokens = inner.formula.replace('*', ' * ').replace('/', ' / ').split()
                        cleaned_tokens = []
                        for i in range(len(tokens)):
                            if tokens[i] in parameters_dict:
                                tokens[i] = parameters_dict[tokens[i]]
                        tokens = replace_min(tokens)
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
                        lead_time = safe_float(tarif.lead_time)
                        preporation_time = safe_float(tarif.preporation_time)
                        min_time = safe_float(tarif.min_time)
                        many_people = safe_float(tarif.many_people)
                        salary = safe_float(inner_operation.job_title.salary)
                        result_to_done = preporation_time + lead_time * result
                        if result_to_done < min_time:
                            result2 = ((min_time * many_people) / 60) * salary
                        else:
                            result2 = (result_to_done * many_people / 60) * salary
                        print(f"{inner} -- Результат операции: {result2}")
                        total_inner_operations_sum += result2
                total_nomenclature_sum = 0
                for nomenclature in nomenclature_list:
                    nomenclature2 = None  # Инициализируем переменную перед циклом

                    for composition in compositions:
                        # Используем ключ 'operations', так как composition — словарь
                        techoperation = composition['operations']
                        if techoperation.operation_link_name == techlink.operation_link_name:
                            nomenclature2 = composition['nomenclature']
                    # Проверяем, присвоено ли значение nomenclature2, прежде чем сравнивать
                    if nomenclature2 and nomenclature2 == nomenclature:
                        material_operations = MaterialsTechnologicalOperation.objects.filter(
                            nomenklatura=nomenclature,
                            technicological_operation=techlink
                        )
                        for material in material_operations:
                            if material.formula is None:
                                material.formula = techlink.formula
                            replace_formula_with_calculation(material)
                            tokens = material.formula.replace('*', ' * ').replace('/', ' / ').split()
                            cleaned_tokens = [
                                str(parameters_dict.get(token, token)) if token in parameters_dict else token
                                for token in tokens
                            ]
                            final_formula = ' '.join(cleaned_tokens)
                            result = eval(final_formula)
                            default_parameters = ParametersNormativesInCalculation._meta.get_field('overheads').default
                            salary_fund_default = ParametersNormativesInCalculation._meta.get_field('salary_fund').default
                            profit_default = ParametersNormativesInCalculation._meta.get_field('profit').default
                            payroll_default = ParametersNormativesInCalculation._meta.get_field('payroll').default
                            matched_nomenklaturas = []
                            if material.nomenklatura and material.nomenklatura.nomenklatura_name in nomenclature_list:
                                matched_nomenklaturas.append(material.nomenklatura)
                            nomenclature = material.nomenklatura
                            if not nomenclature.price:
                                nomenclature.price = 1
                            if not nomenclature.waste_rate:
                                nomenclature.waste_rate = 1
                            if not nomenclature.material_markup:
                                nomenclature.material_markup = 1
                            nomenclature.price = float(nomenclature.price)
                            nomenclature.waste_rate = float(nomenclature.waste_rate)
                            nomenclature.material_markup = float(nomenclature.material_markup)
                            nomenclature_total = nomenclature.price * nomenclature.waste_rate * nomenclature.material_markup
                            result = nomenclature_total * result
                            total_nomenclature_sum += result
                technological_operation = TechnologicalOperation.objects.filter(operation_link_name=techlink).first()
                adding_materials_operations = AddingMaterialsTechnologicalOperation.objects.filter(technicological_operation=technological_operation)
                total_adding_material_sum = 0
                for adding_material in adding_materials_operations:
                    nomenklatura_price = adding_material.nomenklatura.price
                    if adding_material.formula is None:
                        adding_material.formula = techlink.formula
                    replace_formula_with_calculation(adding_material)
                    tokens = adding_material.formula.replace('*', ' * ').replace('/', ' / ').split()
                    cleaned_tokens = [
                        str(parameters_dict.get(token, token)) if token in parameters_dict else token
                        for token in tokens
                    ]
                    final_formula = ' '.join(cleaned_tokens)
                    result = eval(final_formula)
                    matched_nomenklaturas = []
                    if adding_material.nomenklatura and adding_material.nomenklatura.nomenklatura_name in nomenclature_list:
                        matched_nomenklaturas.append(adding_material.nomenklatura)
                    nomenclature = adding_material.nomenklatura
                    # Суммирование цен номенклатур
                    if not nomenclature.price:
                        nomenclature.price = 1
                    if not nomenclature.waste_rate:
                        nomenclature.waste_rate = 1
                    if not nomenclature.material_markup:
                        nomenclature.material_markup = 1
                    nomenclature.price = float(nomenclature.price)
                    nomenclature.waste_rate = float(nomenclature.waste_rate)
                    nomenclature.material_markup = float(nomenclature.material_markup)
                    nomenclature_total = nomenclature.price * nomenclature.waste_rate * nomenclature.material_markup
                    result = nomenclature_total * result
                    result2 = (
                        result +
                        result * salary_fund_default / 100 +
                        result * profit_default / 100
                    )
                    total_adding_material_sum += result2
                total_sum_operations = total_inner_operations_sum 
                total_sum_materials = total_adding_material_sum + total_nomenclature_sum 
                overheads_default = ParametersNormativesInCalculation._meta.get_field('overheads').default
                salary_fund_default = ParametersNormativesInCalculation._meta.get_field('salary_fund').default
                profit_default = ParametersNormativesInCalculation._meta.get_field('profit').default
                payroll_default = ParametersNormativesInCalculation._meta.get_field('payroll').default
                price_material = total_nomenclature_sum
                print(f"Материалы: {price_material}")
                price_add_material = total_adding_material_sum
                print(f"Дополнительные Материалы: {price_add_material}")
                price_salary = total_sum_operations
                print(f"Заработная плата: {price_salary}")
                price_payroll = total_sum_operations * payroll_default / 100
                print(f"Отчисления на зарплату: {price_payroll}")
                price_overheads = total_sum_operations * overheads_default / 100
                print(f"Накладные расходы: {price_overheads}")
                price_cost = price_material + price_salary + price_overheads + price_payroll
                price_cost_with_add = price_cost + price_add_material
                print(f"Себестоимость: {price_cost}")
                price_profit = price_cost_with_add * profit_default / 100
                print(f"Прибыль: {price_profit}")
                price_salary_fund = price_cost_with_add * salary_fund_default / 100
                print(f"Зарплатный фонд: {price_salary_fund}")
                final_price = price_cost_with_add + price_profit + price_salary_fund
                print(f"Цена: {final_price}")
                price_cost_with_adds += price_cost_with_add
                final_price_current_techoperation += final_price
                operations_prices.append({
                    'operation': techlink.operation_link_name,
                    'final_price': final_price_current_techoperation
                })
                operations_fullprices.append({
                    'operation': techlink.operation_link_name,
                    'price_material': price_material,
                    'price_add_material':price_add_material,
                    'price_salary':price_salary,
                    'price_payroll':price_payroll,
                    'price_overheads':price_overheads,
                    'price_cost':price_cost,
                    'price_profit':price_profit,
                    'price_salary_fund':price_salary_fund,
                    'price_cost_with_add':price_cost_with_add,
                    'final_price':final_price_current_techoperation
                })
            all_final_prices = sum(item['final_price'] for item in operations_prices)
            all_price_material = sum(item['price_material'] for item in operations_fullprices)
            print(f"Общие Материалы: {all_price_material}")
            all_price_add_material = sum(item['price_add_material'] for item in operations_fullprices)
            print(f"Общие Дополнительные материалы: {all_price_add_material}")
            all_price_salary = sum(item['price_salary'] for item in operations_fullprices)
            print(f"Общие Заработная плата: {all_price_salary}")
            all_price_payroll = sum(item['price_payroll'] for item in operations_fullprices)
            print(f"Общие Отчисления на зарплату: {all_price_payroll}")
            all_price_overheads = sum(item['price_overheads'] for item in operations_fullprices)
            print(f"Общие Накладные расходы: {all_price_overheads}")
            all_price_cost = sum(item['price_cost'] for item in operations_fullprices)
            print(f"Общая Себестоимость: {all_price_cost}")
            all_price_profit = sum(item['price_profit'] for item in operations_fullprices)
            print(f"Общая Прибыль: {all_price_profit}")
            all_price_salary_fund = sum(item['price_salary_fund'] for item in operations_fullprices)
            print(f"Общий Зарплатный фонд: {all_price_salary_fund}")
            all_price_cost_with_add = sum(item['price_cost_with_add'] for item in operations_fullprices)
            print(f"Общая Себестоимость с дополнительными материалами: {all_price_cost_with_add}")
            all_final_price = sum(item['final_price'] for item in operations_fullprices)
            print(f"Общая Итоговая цена: {all_final_price}")
            price_cost_with_adds += price_cost_with_adds
            default_parameters = ParametersNormativesInCalculation._meta.get_field('overheads').default
            salary_fund_default = ParametersNormativesInCalculation._meta.get_field('salary_fund').default
            profit_default = ParametersNormativesInCalculation._meta.get_field('profit').default
            payroll_default = ParametersNormativesInCalculation._meta.get_field('payroll').default
            response_data = {
                'success': True,
                'total_nomenclature': price_cost_with_adds,
                'total_final_price': all_final_prices,
                'operations': operations_prices,
                'default_parameters': {
                    'overheads': default_parameters,
                    'salary_fund': salary_fund_default,
                    'profit': profit_default,
                    'payroll': payroll_default
                }
            }
            return JsonResponse(response_data)

        except Exception as e:
            print("Ошибка при обработке запроса:", e)
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'}, status=405)

def is_token_expired(user_data):
    """Проверяет, истёк ли access_token"""
    if not user_data.expires_at:
        return True  # Если expires_at не задан, считаем токен просроченным
    return timezone.now() >= user_data.expires_at

def get_valid_token(user_data):
    """Получает валидный токен, обновляя его при необходимости"""
    if is_token_expired(user_data):
        return refresh_bitrix_token(user_data.refresh_token)
    return user_data.auth_token

import os
import logging
import requests
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone

# Настройка логирования для диагностики
logger = logging.getLogger(__name__)

REDIRECT_URI = "https://reklamaoko.ru/static/update_tokens.php"  # Ваш redirect_uri
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# @csrf_exempt
# def create_deal(request):
#     print('сделка')
#     if request.method == 'POST':
#         user_id = request.user.id  # Получите идентификатор текущего пользователя (или передайте его в запросе)
#         print(user_id)
#         data = json.loads(request.body)
#         price = data.get('price')
#         # price = request.POST.get('price')  # Получите цену из запроса
#         print(price)

#         if not price:
#             return JsonResponse({'error': 'Price not provided'}, status=400)
        
#         try:
#             user_data = BitrixUser.objects.all().first()
#             print(user_data)
#             # Проверяем, истёк ли токен
#             if is_token_expired(user_data):
#                 print('тут')
#                 access_token = refresh_bitrix_token(user_data.refresh_token)
#             else:
#                 print('тут2')

#                 access_token = user_data.auth_token

#             # Формируем запрос
#             deal_data = {
#                 "fields": {
#                     "TITLE": "Сделка по калькуляции",
#                     "OPPORTUNITY": float(price),
#                     "CURRENCY_ID": "RUB",
#                     "STAGE_ID": "NEW",
#                 }
#             }
#             url = f"https://{user_data.domain}/rest/crm.deal.add.json"
#             headers = {
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             }
#             response = requests.post(url, json=deal_data, headers=headers)
#             response_data = response.json()

#             if "result" in response_data:
#                 return JsonResponse({'message': 'Deal created successfully', 'deal_id': response_data['result']})
#             else:
#                 return JsonResponse({'error': response_data.get('error_description', 'Unknown error')}, status=400)

#         except BitrixUser.DoesNotExist:
#             return JsonResponse({'error': 'User not registered in Bitrix'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_deal(request):
    """Создание сделки в Bitrix CRM."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        # Получение данных из запроса
        data = json.loads(request.body)
        price = data.get('price')

        if not price:
            return JsonResponse({'error': 'Price not provided'}, status=400)

        # Проверяем, зарегистрирован ли пользователь в Bitrix
        user_data = BitrixUser.objects.first()
        if not user_data:
            return JsonResponse({'error': 'User not registered in Bitrix'}, status=404)

        # Проверяем, истек ли токен доступа
        access_token = None
        if is_token_expired(user_data):
            try:
                access_token = refresh_bitrix_token(user_data.refresh_token)
            except Exception as e:
                logger.error(f"Ошибка обновления токена: {str(e)}")
                # Если токен недействителен, генерируем URL для авторизации
                if "invalid_grant" in str(e):
                    logger.info("Недействительный refresh token. Требуется повторная авторизация.")
                    auth_url = get_authorization_url()
                    return JsonResponse({
                        "error": "Authorization required. Please reauthorize the application.",
                        "authorization_url": auth_url
                    }, status=401)
        else:
            access_token = user_data.auth_token

        # Если access_token недоступен, требуется авторизация
        if not access_token:
            auth_url = get_authorization_url()
            return JsonResponse({
                "error": "Authorization required. Please reauthorize the application.",
                "authorization_url": auth_url
            }, status=401)

        # Формирование данных для создания сделки
        deal_data = {
            "fields": {
                "TITLE": "Сделка по калькуляции",
                "OPPORTUNITY": float(price),
                "CURRENCY_ID": "RUB",
                "STAGE_ID": "NEW",
            }
        }

        # Отправка запроса в Bitrix CRM
        url = f"https://{user_data.domain}/rest/crm.deal.add.json"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=deal_data, headers=headers)
        response_data = response.json()

        # Обработка ответа от Bitrix
        if "result" in response_data:
            return JsonResponse({'message': 'Deal created successfully', 'deal_id': response_data['result']})
        else:
            return JsonResponse({'error': response_data.get('error_description', 'Unknown error')}, status=400)

    except BitrixUser.DoesNotExist:
        return JsonResponse({'error': 'User not registered in Bitrix'}, status=404)
    except Exception as e:
        logger.error(f"Ошибка при создании сделки: {str(e)}")
        # Обработка недействительного refresh token
        if "invalid_grant" in str(e):
            auth_url = get_authorization_url()
            return JsonResponse({
                "error": "Authorization required. Please reauthorize the application.",
                "authorization_url": auth_url
            }, status=401)

        return JsonResponse({'error': str(e)}, status=500)




def get_authorization_url():
    """Генерация URL для авторизации."""

    auth_url = f"https://oauth.bitrix.info/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    logger.info(f"Redirecting user to authorization URL: {auth_url}")
    return auth_url

def refresh_bitrix_token(refresh_token):
    """Обновление токена через refresh_token."""
    try:
        user_data = BitrixUser.objects.get(refresh_token=refresh_token)
        if user_data.is_refresh_token_expired():
            raise Exception("Refresh token has expired. Please reauthorize the application.")

        # Запрос на обновление токена
        url = "https://oauth.bitrix.info/oauth/token/"
        params = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }

        response = requests.post(url, data=params)
        data = response.json()
        logger.info(f"Response from Bitrix: {data}")

        # Если успешно, обновляем токены
        if "access_token" in data:
            user_data.auth_token = data["access_token"]
            user_data.refresh_token = data["refresh_token"]
            user_data.save()
            return data["access_token"]
        else:
            error_description = data.get("error_description", "Unknown error")
            if data.get("error") == "invalid_grant":
                raise Exception("invalid_grant: Refresh token недействителен.")
            else:
                raise Exception(f"Ошибка обновления токена: {error_description}")

    except Exception as e:
        logger.error(f"Ошибка при обновлении токена: {str(e)}")
        
        # Обработка ошибки недействительного refresh_token
        if "invalid_grant" in str(e):
            logger.error("Refresh token недействителен, требуется авторизация.")
            auth_url = get_authorization_url()  # Генерация URL для авторизации
            logger.info(f"Authorization URL: {auth_url}")  # Логируем ссылку для авторизации
            # Убедитесь, что возвращаем правильный ответ с ссылкой на авторизацию
            return JsonResponse({
                "error": "Authorization required. Please reauthorize the application.",
                "authorization_url": auth_url
            }, status=401)
        
        raise e


def get_user_current(request):
    """Получение информации о текущем пользователе."""
    try:
        # Получаем URL для редиректа после авторизации (если передан)
        redirect_url = request.GET.get('redirect_url', '/')
        
        # Получаем данные о пользователе
        user_data = BitrixUser.objects.all().first()
        if not user_data:
            return JsonResponse({"error": "Пользователь не найден"}, status=404)

        access_token = user_data.auth_token
        refresh_token = user_data.refresh_token
        logger.info(f"Access token: {access_token}")

        # Проверка на истечение срока действия токена
        if is_token_expired(user_data):
            logger.info("Токен доступа истёк. Попытка обновления.")
            access_token = refresh_bitrix_token(refresh_token)  # Эта функция может вернуть ссылку для авторизации

        if isinstance(access_token, JsonResponse):
            # Если access_token вернул JsonResponse, это значит, что требуется авторизация
            logger.info("Необходима повторная авторизация.")
            
            return JsonResponse({
                "authorization_url": get_authorization_url(),
                "redirect_url": redirect_url
            }, status=401)  # Возвращаем URL для авторизации и ссылку для возврата после
        # Запрос к Bitrix24 API для получения информации о текущем пользователе
        url = f"https://{user_data.domain}/rest/user.current.json"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        response_data = response.json()
        logger.info(f"Response from Bitrix: {response_data}")

        if "result" in response_data:
            return JsonResponse({"user_info": response_data["result"]})  # Отправка данных в фронтэнд
        else:
            return JsonResponse({"error": "Ошибка получения информации о пользователе"}, status=400)

    except Exception as e:
        logger.error(f"Ошибка при получении данных пользователя: {str(e)}")

        # Если ошибка связана с недействительным refresh token, генерируем URL для повторной авторизации
        if "invalid_grant" in str(e):
            logger.error("Refresh token недействителен, требуется повторная авторизация.")
            auth_url = get_authorization_url()  # Генерация URL для авторизации
            return JsonResponse({
                "error": "Токен недействителен, требуется повторная авторизация",
                "auth_url": auth_url,
                "redirect_url": redirect_url
            }, status=401)

        return JsonResponse({"error": str(e)}, status=500)

