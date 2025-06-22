"""
This script defines domain-objects classes to capture all logic data of the whole app.
"""
from datetime import datetime
from pydantic import BaseModel


class Todo(BaseModel):
    """This class is used to create Todo instances
    It has five attributes including title, description, is_completed, is_deleted and creation.
    """
    title: str
    description: str
    is_completed: bool = False
    id_deleted: bool = False
    creation: int = int(datetime.timestamp(datetime.now()))
