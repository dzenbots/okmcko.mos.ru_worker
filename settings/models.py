from pydantic import BaseModel


class FileEntry(BaseModel):
    filename: str
    comment: str
