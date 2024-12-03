from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Bitrix_Goods, Bitrix_GoodsComposition, Birtrix_Price_GoodsComposition, Bitrix_GoodsParametersInCalculation, BitrixDeal
from base.models import ParametersOfProducts
from django.http import JsonResponse
import requests
from dateutil import parser
from django.utils.timezone import make_aware
from django.utils.timezone import is_naive

# Create your views here.
@csrf_exempt
def calculation_list(request):
    deal_id = None
    if request.method == "POST":
        try:
            # Проверяем Content-Type
            if request.content_type == "application/json":
                # Если данные в формате JSON
                data = json.loads(request.body)
            elif request.content_type == "application/x-www-form-urlencoded":
                # Если данные передаются как x-www-form-urlencoded
                parsed_data = parse_qs(request.body.decode('utf-8'))
                # Конвертируем значения в обычный словарь (берем только первое значение из списка)
                data = {key: value[0] for key, value in parsed_data.items()}
            else:
                return JsonResponse({"error": "Unsupported Content-Type"}, status=400)

            # Логика обработки данных
            deal_id = data.get("deal_id") or json.loads(data.get("PLACEMENT_OPTIONS", "{}")).get("ID")
            BITRIX_WEBHOOK_URL_CURRECT_DEAL = "https://oko.bitrix24.ru/rest/7/5c7fk7e5y2cev81a/crm.deal.get.json"
        except json.JSONDecodeError as e:
            return JsonResponse({
                "error": "Некорректный JSON",
                "details": str(e),
                "raw_body": request.body.decode('utf-8')  # Тело запроса для анализа
            }, status=400)
        except Exception as e:
            return JsonResponse({"error": "Неизвестная ошибка", "details": str(e)}, status=500)

    if deal_id:
        try:
            # Попробуем найти сделку в базе данных
            deal = BitrixDeal.objects.filter(bitrix_id=deal_id).first()
        except Exception as e:
            # Если ошибка возникает, возвращаем больше информации о проблеме
            return JsonResponse({
                "error": "Database query failed while retrieving deal.",
                "details": str(e),
                "deal_id": deal_id,
            }, status=500)

        if not deal:
            response = requests.get(BITRIX_WEBHOOK_URL_CURRECT_DEAL, params={"id": deal_id})
            if response.status_code != 200:
                return JsonResponse({
                    'error': f"Не удалось получить данные сделки из Bitrix24, код ответа: {response.status_code}"
                }, status=500)

            deal_data = response.json()
            if "result" not in deal_data:
                return JsonResponse({'error': "Сделка не найдена в Bitrix24."}, status=404)

            deal_info = deal_data["result"]
            raw_date_create = deal_info["DATE_CREATE"]
            parsed_date_create = parser.parse(raw_date_create)
            date_create = make_aware(parsed_date_create) if is_naive(parsed_date_create) else parsed_date_create

            raw_date_modify = deal_info["DATE_MODIFY"]
            parsed_date_modify = parser.parse(raw_date_modify)
            date_modify = make_aware(parsed_date_modify) if is_naive(parsed_date_modify) else parsed_date_modify

            deal = BitrixDeal.objects.create(
                bitrix_id=int(deal_id),
                title=deal_info.get("TITLE", "Без названия"),
                stage_id=deal_info.get("STAGE_ID"),
                probability=deal_info.get("PROBABILITY"),
                opportunity=deal_info.get("OPPORTUNITY"),
                currency_id=deal_info.get("CURRENCY_ID"),
                date_created=date_create,
                date_modified=date_modify,
            )
            print(f"Создана новая сделка ID = {deal_id}: {deal.title}")
        
        # Фильтруем связанные калькуляции
        calculations = Bitrix_Calculation.objects.filter(deal=deal)
    else:
        calculations = Bitrix_Calculation.objects.none()  # Если ID сделки нет, показываем пустой список

    # Формируем данные для шаблона
    calculation_data = []
    for calc in calculations:
        calculation_data.append({
            'date': calc.created_at.strftime('%d.%m.%Y') if hasattr(calc, 'created_at') else 'Неизвестная дата',
            'number': calc.id if calc.id else '00000',
            # 'client': calc.client.name if hasattr(calc.client, 'name') else 'Неизвестный клиент',
            # 'manager': calc.manager.name if hasattr(calc.manager, 'name') else 'Неизвестный менеджер',
            'name': calc.name if calc.name else 'Без названия',
            'total_price': calc.price_final_price if calc.price_final_price else '0 руб.',
        })

    # Рендерим HTML
    return render(request, 'calculation_list.html', {'calculations': calculation_data})

@csrf_exempt
def calculation_add(request):
    goods_compositions_data = []
    parameters_data = []
    goods_data = []
    first_good = None
    first_good_id = None
    first_good_name = None
    calc_number = request.GET.get('calc_number', '')
    if calc_number:
        
        calculation = get_object_or_404(Bitrix_Calculation, id=calc_number)
        calculation_name = calculation.name
        # Получаем все композиции товаров для текущей калькуляции
        price_compositions = Birtrix_Price_GoodsComposition.objects.filter(calculation=calculation)

        # Инициализируем две переменные для хранения данных


        # Проходим по всем price_compositions
        for composition in price_compositions:
            # Получаем объект Bitrix_GoodsComposition, связанный с composition
            goods_composition = composition.goods_compostion
            select_goods = goods_composition.goods
            if goods_composition:
                # Добавляем в goods_compositions_data пару "name_type_of_goods - type_of_goods"
                goods_compositions_data.append({
                    goods_composition.name_type_of_goods: goods_composition.type_of_goods
                })
                    # Проверяем, что товар существует
            if select_goods:
                # Сохраняем первый товар в переменную (если еще не сохранен)
                if first_good is None:
                    first_good_id = select_goods.id  # Наименование товара
                    first_good_name = select_goods.bitrix_goods_name  # Наименование товара
                goods_data.append(select_goods.bitrix_goods_name)  # Наименование товара для Битрикс
            else:
                goods_data.append("No goods found")
                
            goods_data.append(select_goods.bitrix_goods_name)
            # Получаем связанные параметры для этой калькуляции
            parameters_in_calculation = Bitrix_GoodsParametersInCalculation.objects.filter(calculation=calculation)

            # Проходим по каждому параметру
            for parameter in parameters_in_calculation:
                if parameter.parameters:
                    # Добавляем в parameters_data пару "parameter_name - parameter_value"
                    parameters_data.append({
                        parameter.parameters.parameters_product: parameter.parameter_value
                    })

        # Теперь у нас есть две переменные:
        # goods_compositions_data с парами "name_type_of_goods - type_of_goods"
        # parameters_data с парами "parameter_name - parameter_value"

        # Можно выводить или использовать их дальше
        print("Goods Compositions:", goods_compositions_data)
        print("Parameters Data:", parameters_data)

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
    return render(request, "calculation_add.html", {"goods": goods, "grouped_compositions": grouped_compositions, 'calc_number':calc_number, 'goods_compositions_data':goods_compositions_data, 'parameters_data':parameters_data, 'first_good_id': first_good_id, 'first_good_name': first_good_name, 'calculation_name':calculation_name})


import logging
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from base.models import BitrixUser  # Предполагаем, что у вас есть модель для хранения данных о пользователе Bitrix
logger = logging.getLogger(__name__)
import os
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')  # Ваш redirect_uri
from base import views

def refresh_bitrix_token(refresh_token):
    print('рефреш токен')
    logger.debug("рефреш токен")

    url = "https://oauth.bitrix.info/oauth/token/"

    """Обновление токена через refresh_token."""
    try:
        params = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        user_data = BitrixUser.objects.get(refresh_token=refresh_token)
        # print(user_data)
        # print(params)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Выбрасывает исключение, если статус ответа не 200
            data = response.json()
            # print("Ответ от API Bitrix24:")
            logger.debug(f"Ответ от API Bitrix24: {data}")
            print(data)
            return data
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
            logger.debug(f"Ошибка при выполнении запроса: {e}")

        if user_data.is_refresh_token_expired():
            raise Exception("Refresh token has expired. Please reauthorize the application.")
        # print(user_data.is_refresh_token_expired())
        # Запрос на обновление токена
        params = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        # print(params)
        response = requests.post(url, data=params)
        # print(response)
        data = response.json()
        print(data)
        logger.debug(f"Response from Bitrix: {data}")
        # print(f"Response from Bitrix: {data}")

        # Если успешно, обновляем токены
        if "access_token" in data:
            user_data.auth_token = data["access_token"]
            user_data.refresh_token = data["refresh_token"]
            user_data.save()
            return data["access_token"]
        else:
            error_description = data.get("error_description")
            print('ошибка:' + error_description)
            logger.debug(f"ошибка {data}")

            if data.get("error") == "invalid_grant":
                raise Exception("invalid_grant: Refresh token недействителен.")
            elif data.get("error") == "invalid_client":
                raise Exception("invalid_cliens: Недействительный клиент, нужна регистрация.")
            else:
                raise Exception(f"Ошибка обновления токена: {error_description}")

    except Exception as e:
        print(f"Ошибка при обновлении токена: {str(e)}")
        logger.debug(f"Ошибка при обновлении токена: {str(e)}")

        # Обработка ошибки недействительного refresh_token
        if "invalid_grant" in str(e):
            logger.debug("Refresh token недействителен, требуется авторизация.")
            auth_url = get_authorization_url()  # Генерация URL для авторизации
            logger.debug(f"Authorization URL: {auth_url}")  # Логируем ссылку для авторизации
            # Убедитесь, что возвращаем правильный ответ с ссылкой на авторизацию
            return JsonResponse({
                "error": "Authorization required. Please reauthorize the application.",
                "authorization_url": auth_url
            }, status=401)
        if "invalid_client" in str(e):
            logger.error("invalid_cliens: Недействительный клиент, нужна регистрация")
            auth_url = get_authorization_url()  # Генерация URL для авторизации
            logger.info(f"Authorization URL: {auth_url}")  # Логируем ссылку для авторизации
            # Убедитесь, что возвращаем правильный ответ с ссылкой на авторизацию
            return JsonResponse({
                "error": "Authorization required. Please reauthorize the application.",
                "authorization_url": auth_url
            }, status=401)
        
        raise e


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

def get_authorization_url():
    """Генерация URL для авторизации."""

    auth_url = f"https://oauth.bitrix.info/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    logger.info(f"Redirecting user to authorization URL: {auth_url}")
    return auth_url


@csrf_exempt
def authoritation(request):
    print('тут')
    if request.method not in ['GET', 'POST']:
        logger.warning(f"Invalid request method: {request.method}")
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        # Если это POST-запрос, обработаем установку данных пользователя
        if request.method == 'POST':
            logger.info("Processing user setup via POST request...")
            
            # Чтение параметров из POST
            domain = request.POST.get('DOMAIN')
            auth_token = request.POST.get('AUTH_ID')
            refresh_token = request.POST.get('REFRESH_ID')
            member_id = request.POST.get('member_id')
            expires_in = request.POST.get('AUTH_EXPIRES')  # Время действия токена в секундах
            # print(domain)
            # print(member_id)
            # Проверка обязательных параметров
            if not all([domain, auth_token, refresh_token, member_id]):
                logger.error("Missing required parameters for user setup.")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Необходимые параметры не получены',
                }, status=400)

            # Расчет времени истечения токена
            expires_at = None
            if expires_in:
                try:
                    expires_in = int(expires_in)
                    expires_at = timezone.now() + timedelta(seconds=expires_in)
                except ValueError:
                    logger.warning("Invalid AUTH_EXPIRES value received.")
                    expires_in = None

            # Сохранение или обновление записи пользователя
            bitrix_user, created = BitrixUser.objects.update_or_create(
                member_id=member_id,
                defaults={
                    'domain': domain,
                    'auth_token': auth_token,
                    'refresh_token': refresh_token,
                    'expires_at': expires_at,
                    'refresh_token_created_at': timezone.now(),
                }
            )

            logger.info(f"User {'created' if created else 'updated'}: {bitrix_user}")
            return JsonResponse({
                'status': 'success',
                'message': 'Данные пользователя сохранены.',
            }, status=200)

        # Если это GET-запрос, проверим данные пользователя и вернем имя и bitrix_id
        logger.info("Checking if user exists in Bitrix...")
        user_data = BitrixUser.objects.first()
        # print(user_data)
        if not user_data:
            logger.error("User not found in Bitrix")
            return JsonResponse({'error': 'User not registered in Bitrix'}, status=404)

        logger.info("Checking if token is expired...")
        access_token = None
        if is_token_expired(user_data):
            logger.info("Token is expired, attempting to refresh...")
            try:
                access_token = refresh_bitrix_token(user_data.refresh_token)
            except Exception as e:
                logger.error(f"Error refreshing token: {str(e)}")
                if "invalid_grant" in str(e):
                    logger.info("Invalid refresh token. Reauthorization required.")
                    auth_url = get_authorization_url()
                    return JsonResponse({
                        "error": "Authorization required. Please reauthorize the application.",
                        "authorization_url": auth_url
                    }, status=401)
        else:
            logger.info("Token is valid.")
            access_token = user_data.auth_token

        if not access_token:
            logger.warning("Access token is missing, authorization required.")
            auth_url = get_authorization_url()
            # print(auth_url)
            return JsonResponse({
                "error": "Authorization required. Please reauthorize the application.",
                "authorization_url": auth_url
            }, status=401)

        logger.info("Sending request to Bitrix CRM to get user info...")
        url = f"https://{user_data.domain}/rest/user.current.json"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response_data = response.json()
        logger.info(f"Response from Bitrix: {response_data}")

        if "result" in response_data:
            user_info = response_data["result"]
            user_name = user_info.get("NAME", "Unknown") + " " + user_info.get("LAST_NAME", "Unknown")
            bitrix_id = user_info.get("ID", None)  # Получаем Bitrix ID

            # Обновляем или сохраняем Bitrix ID в модели
            if user_data:
                user_data.bitrix_id = bitrix_id  # Обновляем bitrix_id
                user_data.save()

            logger.info(f"User name: {user_name}, Bitrix ID: {bitrix_id}")

            return JsonResponse({
                'user_name': user_name,
                'bitrix_id': bitrix_id  # Отправляем Bitrix ID в ответе
            })
        else:
            error_description = response_data.get('error_description', 'Unknown error')
            print(f"Error from Bitrix: {error_description}")
            return JsonResponse({'error': error_description}, status=400)

    except Exception as e:
        logger.error(f"Error retrieving user info: {str(e)}")
        if "invalid_grant" in str(e):
            auth_url = get_authorization_url()
            return JsonResponse({
                "error": "Authorization required. Please reauthorize the application.",
                "authorization_url": auth_url
            }, status=401)
        return JsonResponse({'error': str(e)}, status=500)
import logging
from django.http import JsonResponse
import requests
import os
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlparse, parse_qs

# Логгер для диагностики
logger = logging.getLogger(__name__)

def bitrix_callback(request):
    # Извлекаем код авторизации из параметров GET-запроса
    auth_code = request.GET.get('code')

    if not auth_code:
        logger.error('Не получен код авторизации')
        return JsonResponse({
            'status': 'error',
            'message': 'Не получен код авторизации.'
        })

    logger.info(f"Получен код авторизации: {auth_code}")

    # Извлекаем другие параметры из URL
    parsed_url = urlparse(request.build_absolute_uri())
    query_params = parse_qs(parsed_url.query)
    url_data = {
        "code": query_params.get("code", [None])[0],
        "state": query_params.get("state", [None])[0],
        "domain": query_params.get("domain", [None])[0],
        "member_id": query_params.get("member_id", [None])[0],
        "scope": query_params.get("scope", [None])[0],
        "server_domain": query_params.get("server_domain", [None])[0]
    }

    token_url = 'https://oauth.bitrix24.ru/oauth/token/'
    params = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'code': url_data.get("code"),
        'grant_type': 'authorization_code',
        'redirect_uri': os.getenv('REDIRECT_URI'),
    }

    try:
        # Логируем параметры перед запросом
        logger.info(f"Параметры запроса: {params}")
        
        # Выполняем запрос для получения токенов
        response = requests.get(token_url, params=params)

        # Логируем полный ответ от API
        logger.info(f"Ответ от API Bitrix: {response.status_code} - {response.text}")

        # Проверяем, что ответ был успешным и содержит необходимые данные
        if response.status_code != 200:
            logger.error(f"Ошибка запроса: Статус код {response.status_code}. Ответ: {response.text}")
            return JsonResponse({
                'status': 'error',
                'message': f"Ошибка запроса: {response.status_code} - {response.text}",
                'response_data': response.json(),  # Добавляем данные ответа
                'url_data': url_data  # Добавляем данные из URL
            })

        token_data = response.json()
        
        # Логируем данные ответа
        logger.info(f"Полученные данные: {token_data}")
        
        if 'access_token' not in token_data:
            error_message = token_data.get('error_description', 'Не найден access_token в ответе')
            print(f"Ошибка: {error_message}")
            return JsonResponse({
                'status': 'error',
                'message': error_message,
                'response_data': token_data,  # Добавляем данные ответа
                'url_data': url_data  # Добавляем данные из URL
            })

        # Если токен получен успешно
        access_token = token_data['access_token']
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 3600)
        expires_at = timezone.now() + timedelta(seconds=expires_in)

        logger.info(f"Токены получены: {access_token} | {refresh_token}")
        logger.info(f"Время истечения: {expires_at}")

        return JsonResponse({
            'status': 'success',
            'message': 'Токены успешно получены и сохранены.',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': expires_in,
            'auth_code': auth_code,  # Добавляем данные из URL
            'url_data': url_data  # Добавляем данные из URL
        })

    except requests.RequestException as e:
        # Логируем исключение, если запрос не удался
        logger.error(f"Ошибка запроса к Bitrix: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f"Ошибка при запросе к Bitrix API: {e}",
            'error_details': str(e),  # Добавляем текст ошибки
            'auth_code': auth_code,  # Добавляем данные из URL
            'url_data': url_data,  # Добавляем данные из URL
            'response.status_code': response.status_code  # Добавляем данные из URL
        })
    except Exception as e:
        # Логируем другие исключения
        logger.error(f"Неизвестная ошибка: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f"Неизвестная ошибка: {e}",
            'error_details': str(e),  # Добавляем текст ошибки
            'auth_code': auth_code,  # Добавляем данные из URL
            'url_data': url_data  # Добавляем данные из URL
        })
    
import json
from bitrix_calc.models import Bitrix_Calculation

BITRIX_WEBHOOK_URL_DEALS = "https://oko.bitrix24.ru/rest/7/5c7fk7e5y2cev81a/crm.deal.list"

@csrf_exempt
def create_calculation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)

            calculation_name = data.get('name')
            operations_fullprices = data.get('operations_fullprices')
            parameters_dict = data.get('parameters_dict')
            dealId = data.get('dealId')
            
            print(operations_fullprices)  # Принт для отладки

            if not calculation_name:
                return JsonResponse({'error': 'Название калькуляции обязательно.'}, status=400)
            
            if not dealId:
                return JsonResponse({'error': 'dealId обязателен.'}, status=400)

            # Проверяем наличие сделки в базе
            deal = BitrixDeal.objects.filter(bitrix_id=dealId).first()

            if not deal:
                # Если сделки нет, получаем ее данные из Bitrix24 и создаем
                response = requests.get(BITRIX_WEBHOOK_URL_DEALS, params={"id": dealId})
                if response.status_code != 200:
                    return JsonResponse({'error': f"Не удалось получить данные сделки из Bitrix24, код ответа: {response.status_code}"}, status=500)

                deal_data = response.json()
                if "result" not in deal_data:
                    return JsonResponse({'error': "Сделка не найдена в Bitrix24."}, status=404)

                deal_info = deal_data["result"]
                raw_date_create = deal_info["DATE_CREATE"]
                parsed_date_create = parser.parse(raw_date_create)
                date_create = make_aware(parsed_date_create) if is_naive(parsed_date_create) else parsed_date_create

                raw_date_modify = deal_info["DATE_MODIFY"]
                parsed_date_modify = parser.parse(raw_date_modify)
                date_modify = make_aware(parsed_date_modify) if is_naive(parsed_date_modify) else parsed_date_modify

                deal = BitrixDeal.objects.create(
                    bitrix_id=int(dealId),
                    title=deal_info.get("TITLE", "Без названия"),
                    stage_id=deal_info.get("STAGE_ID"),
                    probability=deal_info.get("PROBABILITY"),
                    opportunity=deal_info.get("OPPORTUNITY"),
                    currency_id=deal_info.get("CURRENCY_ID"),
                    date_created=date_create,
                    date_modified=date_modify,
                )
                print(f"Создана новая сделка ID = {dealId}: {deal.title}")

            # Создаем объект калькуляции
            calculation = Bitrix_Calculation.objects.create(
                name=calculation_name,
                deal=deal,
                price_material=data.get('price_material'),
                price_add_material=data.get('price_add_material'),
                price_salary=data.get('price_salary'),
                price_payroll=data.get('price_payroll'),
                price_overheads=data.get('price_overheads'),
                price_cost=data.get('price_cost'),
                price_profit=data.get('price_profit'),
                price_salary_fund=data.get('price_salary_fund'),
                price_final_price=data.get('price_final_price'),
            )

            # Обработка операций
            for item in operations_fullprices:
                goods_composition = Bitrix_GoodsComposition.objects.filter(id=item.get('composition_of_techoperation')).first()
                if not goods_composition:
                    print(f"Состав товара с id {item.get('composition_of_techoperation')} не найден.")
                    continue

                Birtrix_Price_GoodsComposition.objects.create(
                    calculation=calculation,
                    goods_compostion=goods_composition,
                    price_material=item.get('price_material'),
                    price_add_material=item.get('price_add_material'),
                    price_salary=item.get('price_salary'),
                    price_payroll=item.get('price_payroll'),
                    price_overheads=item.get('price_overheads'),
                    price_cost=item.get('price_cost'),
                    price_profit=item.get('price_profit'),
                    price_salary_fund=item.get('price_salary_fund'),
                    price_final_price=item.get('final_price'),
                )

            # Обработка параметров
            for formula_name, value in parameters_dict.items():
                try:
                    parameter = ParametersOfProducts.objects.get(formula_name=formula_name)
                    Bitrix_GoodsParametersInCalculation.objects.create(
                        calculation=calculation,
                        parameters=parameter,
                        parameter_value=str(value)
                    )
                except ParametersOfProducts.DoesNotExist:
                    print(f"Parameter with formula_name='{formula_name}' not found.")

            return JsonResponse({'id': calculation.id, 'name': calculation.name}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Недопустимый метод.'}, status=405)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Bitrix_Calculation


@csrf_exempt
def delete_calculation(request, pk):
    if request.method == "POST":
        try:
            calculation = get_object_or_404(Bitrix_Calculation, pk=pk)
            calculation.delete()  # Удаляет объект и связанные записи благодаря CASCADE
            return JsonResponse({"status": "success", "message": "Калькуляция успешно удалена."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Ошибка удаления: {str(e)}"})
    else:
        return JsonResponse({
            "status": "error",
            "message": "Неподдерживаемый метод запроса." + str(request.method) + str(pk),
            "pk": pk,
            "method_received": request.method,
        })