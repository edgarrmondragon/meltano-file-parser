from models.base import BaseModel


class Command(BaseModel):
    args: str
    executable: str = None
    description: str = None
