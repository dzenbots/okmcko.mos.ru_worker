from pydantic import Field
from config.env_config.main import BaseConfig, DatabaseConfig, EmailConfig, Miscellaneous, MosRuConfig, Notifications, StorageConfig, TelegramConfig


class Config(BaseConfig):
    mos_ru: MosRuConfig = Field(default_factory=MosRuConfig)
    notifications: Notifications = Field(default_factory=Notifications)
    email: EmailConfig = Field(default_factory=EmailConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    misc: Miscellaneous = Field(default_factory=Miscellaneous)

    @classmethod
    def load(cls) -> 'Config':
        return cls()


if __name__ == '__main__':
    print(Config.load())
