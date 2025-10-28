from peewee import SqliteDatabase

from config import config

db = SqliteDatabase(config.database.filename)

from database.models import File, initialize_db, close_db

__all__ = [
    "File",
    "initialize_db",
    "close_db",
    "db"
]
