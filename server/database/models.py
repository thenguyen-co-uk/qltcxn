"""
This script defines domain-objects classes to capture all logic data of the app.
"""
from datetime import date, datetime
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


class Tenant(BaseModel):
    """This class is used to capture the tenant information.
    The resident information includes name, room, dob, etc.
    """
    id: str # identifier to different among residents
    name: str
    dob: date
    gender: str
    room: str
    hb: bool = True # housing benefit
    notes: str # the changes made on the tenant for example: housing benefit
    creation: int = int(datetime.timestamp(datetime.now()))
    modification: int = int(datetime.timestamp(datetime.now()))


class Rent(BaseModel):
    """This class is used to hold all rents
    The rents are all payments weekly or monthly
    """
    tenant_id: str
    week_commence: date
    rent_due: date
    payment_date: date
    standing_order: float
    extra: float
    