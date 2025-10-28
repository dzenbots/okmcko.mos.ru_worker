
from typing import Optional

from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class MosRuConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='mos_ru_')

    login: str
    password: SecretStr


class Notifications(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='notification_')

    email: bool
    telegram: bool


class EmailConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='email_')

    smtp_login: EmailStr
    smtp_password: SecretStr
    smtp_server: str
    smtp_port: int = 465
    target_emails: list[EmailStr]


class TelegramConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='telegram_')

    bot_token: SecretStr
    chat_id: int
    thread_id: Optional[int] = None


class DatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='database_')

    filename: str


class StorageConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='storage_')

    folder_path: str


class Miscellaneous(BaseConfig):
    debug: bool = False
