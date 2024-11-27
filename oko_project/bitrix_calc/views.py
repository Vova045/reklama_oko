from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Bitrix_Goods, Bitrix_GoodsComposition, Birtrix_Price_GoodsComposition, Bitrix_GoodsParametersInCalculation
from base.models import ParametersOfProducts
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
    """Обновление токена через refresh_token."""
    try:
        params = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        user_data = BitrixUser.objects.get(refresh_token=refresh_token)
        print(user_data)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Выбрасывает исключение, если статус ответа не 200
            data = response.json()
            print("Ответ от API Bitrix24:")
            logger.debug(f"Ответ от API Bitrix24: {data}")
            print(data)
            return data
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса: {e}")
        if user_data.is_refresh_token_expired():
            raise Exception("Refresh token has expired. Please reauthorize the application.")
        print(user_data.is_refresh_token_expired())
        # Запрос на обновление токена
        url = "https://oauth.bitrix.info/oauth/token/"
        params = {
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": refresh_token,
        }
        print(params)
        response = requests.post(url, data=params)
        print(response)
        data = response.json()
        print(data)
        logger.debug(f"Response from Bitrix: {data}")
        print(f"Response from Bitrix: {data}")

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
            elif data.get("error") == "invalid_client":
                raise Exception("invalid_cliens: Недействительный клиент, нужна регистрация.")
            else:
                raise Exception(f"Ошибка обновления токена: {error_description}")

    except Exception as e:
        logger.error(f"Ошибка при обновлении токена: {str(e)}")
        
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
            print(auth_url)
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
            logger.error(f"Error from Bitrix: {error_description}")
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
            logger.error(f"Ошибка: {error_message}")
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
@csrf_exempt
def create_calculation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)
            calculation_name = data.get('name')
            operations_fullprices = data.get('operations_fullprices')
            parameters_dict = data.get('parameters_dict')
            print(operations_fullprices)  # Принт для отладки

            if not calculation_name:
                return JsonResponse({'error': 'Название калькуляции обязательно.'}, status=400)

            # Создаем объект калькуляции
            calculation = Bitrix_Calculation.objects.create(
                name=calculation_name,
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

            # Проходим по каждому элементу operations_fullprices
            for item in operations_fullprices:
                # Получаем состав товара по id
                goods_composition = Bitrix_GoodsComposition.objects.filter(id=item.get('composition_of_techoperation')).first()

                if not goods_composition:
                    # Если не нашли товар, пропускаем этот элемент
                    print(f"Состав товара с id {item.get('composition_of_techoperation')} не найден.")
                    continue

                # Создаем запись в Birtrix_Price_GoodsComposition
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
            for formula_name, value in parameters_dict.items():
                    try:
                        # Найти параметр по formula_name
                        parameter = ParametersOfProducts.objects.get(formula_name=formula_name)
                        
                        # Создать экземпляр модели
                        Bitrix_GoodsParametersInCalculation.objects.create(
                            calculation=calculation,
                            parameters=parameter,
                            parameter_value=str(value)  # Преобразуем значение в строку для сохранения
                        )
                    except ParametersOfProducts.DoesNotExist:
                        # Обработать случай, если параметр не найден
                        print(f"Parameter with formula_name='{formula_name}' not found.")


            return JsonResponse({'id': calculation.id, 'name': calculation.name}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Недопустимый метод.'}, status=405)
