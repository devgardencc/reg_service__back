import gspread
import httpx
from config import settings
from logger import logger


class GoogleSheetsService:
    def __init__(self, sheet_id: str):
        self.sheet = None

        credentials = {
            "type": settings.type,
            "project_id": settings.project_id,
            "private_key_id": settings.private_key_id,
            "private_key": settings.private_key,
            "client_email": settings.client_email,
            "client_id": settings.client_id,
            "auth_uri": settings.auth_uri,
            "token_uri": settings.token_uri,
            "auth_provider_x509_cert_url": settings.auth_provider_x509_cert_url,
            "client_x509_cert_url": settings.client_x509_cert_url,
            "universe_domain": settings.universe_domain
        }
        try:
            gc = gspread.service_account_from_dict(credentials)
            sh = gc.open_by_key(sheet_id)
            self.sheet = sh.sheet1
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Sheets: {e}")

    def append_row(self, row_data: list):
        """Синхронная функция для записи (вызывается через threadpool)"""
        if not self.sheet:
            raise RuntimeError("Google Sheets API не инициализирован.")
        self.sheet.append_row(row_data)


class TelegramService:
    def __init__(
        self, telegram_bot_token: str, telegram_chat_id: int, telegram_thread_id: int
    ):
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_thread_id = telegram_thread_id


    async def send_message(self, text: str):
        """Асинхронная отправка сообщения в Telegram"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "message_thread_id": self.telegram_thread_id,
            "text": text,
            "parse_mode": "HTML",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info("Уведомление в Telegram успешно отправлено.")
            except Exception as e:
                logger.error(f"Ошибка при отправке в Telegram: {e}")
