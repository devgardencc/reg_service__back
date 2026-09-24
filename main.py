from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from datetime import datetime, timezone

from fastapi.concurrency import run_in_threadpool
from jinja2 import Environment, FileSystemLoader

from app.scheme import HealthResponse, RegisterRequest, RegisterResponse
from app.config import settings
from app.service import GoogleSheetsService, TelegramService
from app.logger import logger

jinja_env = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)
telegram_template = jinja_env.get_template("telegram_msg.j2")

app = FastAPI(title="Registration API devgardencc", version="0.1")
gs_service = GoogleSheetsService(settings.sheet_id, settings.account)
tg_service = TelegramService(
    settings.telegram_bot_token, settings.telegram_chat_id, settings.telegram_thread_id
)


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc))


@app.post(
    "/api/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
async def register_user(data: RegisterRequest, background_tasks: BackgroundTasks):
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    row_to_insert = [formatted_time, *data.model_dump().values()]

    try:
        await run_in_threadpool(gs_service.append_row, row_to_insert)
        logger.info(f"Запись успешно добавлена в таблицу для {data.name}")
    except Exception as e:
        logger.error(
            f"Критическая ошибка: запись НЕ создана. Уведомление не будет отправлено. Ошибка: {e}"
        )

        raise HTTPException(
            status_code=500, detail="Ошибка базы данных. Регистрация не удалась."
        )

    template_data = {**data.model_dump(), "registered_at": formatted_time}

    message_text = telegram_template.render(**template_data)
        
   

    background_tasks.add_task(tg_service.send_message, message_text)
    return RegisterResponse(name=data.name, created_at=current_time)
