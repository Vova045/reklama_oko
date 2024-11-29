import requests
from django.utils.timezone import make_aware
from datetime import datetime
from bitrix_calc.models import BitrixCompany

# URL вашего вебхука для Bitrix24
BITRIX_WEBHOOK_URL = "https://oko.bitrix24.ru/rest/7/5c7fk7e5y2cev81a/crm.company.list"

# Эта функция будет возвращать данные, а не сохранять их в базе
def fetch_and_save_companies():
    companies_data = []  # Список для хранения данных о компаниях
    
    try:
        start = 0  # Начало пагинации
        while True:
            print(f"Получаем данные с offset: {start}")  # Логирование начала запроса
            response = requests.get(BITRIX_WEBHOOK_URL, params={"start": start})
            
            # Проверка, что ответ от API Bitrix24 корректен
            if response.status_code != 200:
                print(f"Ошибка запроса к Bitrix24, код ответа: {response.status_code}")
                break

            data = response.json()
            print(f"Полученные данные: {data}")  # Логирование полученных данных

            if "result" not in data:
                print("Ошибка получения данных:", data)
                break

            companies = data["result"]
            print(f"Получено компаний: {len(companies)}")  # Логирование количества компаний

            # Сохраняем данные в список
            for company in companies:
                company_data = {
                    "ID": company["ID"],
                    "TITLE": company["TITLE"],
                    "COMPANY_TYPE": company.get("COMPANY_TYPE"),
                    "INDUSTRY": company.get("INDUSTRY"),
                    "REVENUE": company.get("REVENUE"),
                    "ADDRESS": company.get("ADDRESS"),
                    "PHONE": company.get("PHONE"),
                    "EMAIL": company.get("EMAIL"),
                    "ASSIGNED_BY_ID": company.get("ASSIGNED_BY_ID"),
                    "DATE_CREATE": company.get("DATE_CREATE"),
                    "DATE_MODIFY": company.get("DATE_MODIFY"),
                }
                companies_data.append(company_data)  # Добавляем в список

            # Проверка, есть ли следующая страница с данными
            if not data.get("next"):
                break
            start = data.get("next", 0)  # Переход на следующую страницу

        return companies_data  # Возвращаем собранные данные о компаниях

    except Exception as e:
        print("Ошибка синхронизации с Bitrix24:", str(e))
        return []  # Возвращаем пустой список в случае ошибки
