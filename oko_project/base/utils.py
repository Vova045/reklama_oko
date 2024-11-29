import requests
from django.utils.timezone import make_aware
from datetime import datetime
from .models import BitrixCompany

# URL вашего вебхука для Bitrix24
BITRIX_WEBHOOK_URL = "https://oko.bitrix24.ru/rest/7/5c7fk7e5y2cev81a/crm.company.list"

def fetch_and_save_companies():
    try:
        start = 0  # Начало пагинации
        while True:
            # Запрос данных о компаниях из Bitrix24
            response = requests.get(BITRIX_WEBHOOK_URL, params={"start": start})
            data = response.json()

            if "result" not in data:
                print("Ошибка получения данных:", data)
                break

            companies = data["result"]
            for company in companies:
                # Сохранение или обновление данных в базе
                BitrixCompany.objects.update_or_create(
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

            # Проверяем, есть ли следующая страница с данными
            if not data.get("next"):
                break
            start = data["next"]  # Переход на следующую страницу

    except Exception as e:
        print("Ошибка синхронизации с Bitrix24:", str(e))
