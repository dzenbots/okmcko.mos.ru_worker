from pydantic import BaseModel


class FileEntry(BaseModel):
    date: str
    filename: str
    comment: str

