from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    allowed_hosts: list[str] = ["https://join.devgarden.cc"]
    enironment: str
    telegram_bot_token: str
    telegram_chat_id: int
    telegram_thread_id: int
    sheet_id: str

    account: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()