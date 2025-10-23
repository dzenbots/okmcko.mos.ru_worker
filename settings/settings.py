from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LOGIN: str
    PASSWORD: str
    DEBUG: bool
    DWNLD_DIR_PATH: str
    MCKO_BOT_TOKEN: str
    CHAT_ID: str
    MESSAGE_THREAD_ID: str = None
    SMTP_SERVER: str
    SMTP_PORT: str
    SMTP_LOGIN: str
    SMTP_PASSWORD: str
    TARGET_EMAIL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
