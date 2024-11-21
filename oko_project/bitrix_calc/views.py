from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Bitrix_Goods, Bitrix_GoodsComposition
from django.http import JsonResponse
import requests

# Create your views here.
@csrf_exempt
def calculation_list(request):
    return render(request, 'calculation_list.html')

@csrf_exempt
def calculation_add(request):
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
    return render(request, "calculation_add.html", {"goods": goods, "grouped_compositions": grouped_compositions})

import requests

import requests

def get_clients_from_php():
    url = 'https://reklamaoko.ru/static/bitrix_clients.php'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на статус ответа
        return response.json()  # Возвращаем результат в формате JSON
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        raise

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Если необходимо отключить проверку CSRF для этого обработчика
def get_clients(request):
    try:
        clients = get_clients_from_php()  # Получаем данные

        # Логирование полученных данных
        print("Полученные данные от PHP:", clients)

        if isinstance(clients, list):  # Проверяем, что clients - это список
            return JsonResponse({"result": clients}, safe=False)
        else:
            return JsonResponse({"error": "Ошибка: Ответ не является списком"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Ошибка при получении данных: {str(e)}"}, status=500)
