import base64
import json
import re

import gspread
import httpx
from .logger import logger


class GoogleSheetsService:
    def __init__(self, sheet_id: str, account_base64: str):
        self.sheet_id = sheet_id
        self.sheet = None
        try:
            decoded_bytes = base64.b64decode(account_base64)
            creds_info = json.loads(decoded_bytes.decode("utf-8"))
            gc = gspread.service_account_from_dict(creds_info)
            sh = gc.open_by_key(sheet_id)
            self.sheet = sh.sheet1
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Sheets: {e}")

    def append_row(self, row_data: list) -> int:
        """Синхронная функция для записи. Возвращает номер созданной строки."""
        if not self.sheet:
            raise RuntimeError("Google Sheets API не инициализирован.")
        res = self.sheet.append_row(row_data)
        try:
            updated_range = res.get("updates", {}).get("updatedRange", "")
            match = re.search(r"(\d+):[A-Z]+(\d+)$", updated_range) or re.search(r"(\d+)$", updated_range)
            if match:
                return int(match.group(1))
        except Exception as e:
            logger.warning(f"Не удалось распарсить номер строки из res: {e}")

        return len(self.sheet.get_all_values())

    def update_status(self, row_index: int, new_status: str, col_index: int = 10):
        """Обновляет значение в ячейке статуса заданной строки."""
        if not self.sheet:
            raise RuntimeError("Google Sheets API не инициализирован.")
        self.sheet.update_cell(row_index, col_index, new_status)


class TelegramService:
    def __init__(
        self, telegram_bot_token: str, telegram_chat_id: int, telegram_thread_id: int
    ):
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_thread_id = telegram_thread_id

    async def send_message_with_buttons(self, text: str, row_index: int):
        """Отправка сообщения в Telegram с кнопками Принять / Отклонить"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "message_thread_id": self.telegram_thread_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "✅ Принять", "callback_data": f"approve:{row_index}"},
                        {"text": "❌ Отклонить", "callback_data": f"reject:{row_index}"},
                    ]
                ]
            },
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                logger.info("Уведомление с кнопками в Telegram успешно отправлено.")
            except Exception as e:
                logger.error(f"Ошибка при отправке в Telegram: {e}")

    async def answer_callback_query(self, callback_query_id: str, text: str = ""):
        """Ответ Telegram для снятия анимации загрузки на кнопке"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/answerCallbackQuery"
        payload = {"callback_query_id": callback_query_id, "text": text}
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json=payload)
            except Exception as e:
                logger.error(f"Ошибка answerCallbackQuery: {e}")

    async def edit_message_text(self, chat_id: int | str, message_id: int, text: str):
        """Редактирование сообщения в Telegram (удаление кнопок и добавление статуса)"""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": {"inline_keyboard": []},
        }
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json=payload)
                logger.info("Сообщение в Telegram успешно отредактировано.")
            except Exception as e:
                logger.error(f"Ошибка editMessageText: {e}")

