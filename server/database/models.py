from pydantic import BaseModel
from datetime import datetime

class Todo(BaseModel):
    title: str
    description: str
    is_completed: bool = False
    id_deleted: bool = False
    creation: int = int(datetime.timestamp(datetime.now()))