from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Bitrix_Goods, Bitrix_GoodsComposition
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
    return render(request, "home.html", {"goods": goods, "grouped_compositions": grouped_compositions})
