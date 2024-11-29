import requests
from django.utils.timezone import make_aware
from datetime import datetime
from bitrix_calc.models import BitrixCompany

# URL вашего вебхука для Bitrix24
BITRIX_WEBHOOK_URL = "https://oko.bitrix24.ru/rest/7/5c7fk7e5y2cev81a/crm.company.list"

def fetch_and_save_companies():
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

            for company in companies:
                print(f"Обрабатываем компанию: {company}")  # Логирование каждой компании

                # Сохранение или обновление данных в базе
                company_obj, created = BitrixCompany.objects.update_or_create(
                    bitrix_id=company["ID"],
                    defaults={
                        "title": company["TITLE"],
                        "company_type": company.get("COMPANY_TYPE"),
                        "industry": company.get("INDUSTRY"),
                        "revenue": company.get("REVENUE"),
                        "address": company.get("ADDRESS"),
                        "phone": company.get("PHONE"),
                        "email": company.get("EMAIL"),
                        "assigned_by_id": company.get("ASSIGNED_BY_ID"),
                        "date_created": make_aware(datetime.fromisoformat(company["DATE_CREATE"])) if "DATE_CREATE" in company else None,
                        "date_modified": make_aware(datetime.fromisoformat(company["DATE_MODIFY"])) if "DATE_MODIFY" in company else None,
                    }
                )

                if created:
                    print(f"Компания {company['TITLE']} добавлена в базу данных.")
                else:
                    print(f"Компания {company['TITLE']} обновлена в базе данных.")

            # Проверка, есть ли следующая страница с данными
            if not data.get("next"):
                break
            start = data.get("next", 0)  # Переход на следующую страницу

    except Exception as e:
        print("Ошибка синхронизации с Bitrix24:", str(e))