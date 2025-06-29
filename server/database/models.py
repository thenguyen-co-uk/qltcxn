"""
This script defines domain-objects classes to capture all logic data of the app.
"""
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Todo(BaseModel):
    """
    This class is used to create Task instances
    It has five attributes including title, description, is_completed, is_deleted and creation.
    """
    title: str
    description: str
    is_completed: bool = False
    id_deleted: bool = False
    creation: int = int(datetime.timestamp(datetime.now()))


class Tenant(BaseModel):
    """
    This class is used to capture the tenant information.
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
    """
    This class is used to hold all rents
    The rents are all weekly or monthly payments including rent due,
    housing services, utilities and meals.
    """
    tenant_id: str
    week_commence: date
    rent_due: float
    services: float
    utilities: float
    meals: float
    extra: float
    notes: str


class Room(BaseModel):
    """
    This class is used to hold all rooms
    """
    id: str
    name: str
    description: str
    area: str


class IncomeEnum(str, Enum):
    """
    This class is used to define the income types
    """
    STANDING_ORDER = 'Standing Order'
    HOUSING_BENEFIT = 'Housing Benefit'
    REFUND = 'Refund'
    DONATION = 'Donation'
    FUNDING = 'Funding'
    INTEREST = 'Interest'


class Income(BaseModel):
    """
    This class is used to hold all incomes
    """
    for_tenant: str # Tenant ID
    description: str
    amount: float
    # category: Standing Order, Refund, Housing Benefit
    category: IncomeEnum
    # date when the income arrives - this matches with the item on bank
    # statement
    arrived_date: date
    # if the category is Housing Benefit, from_date and to_date are required
    from_date: Optional[date] = None
    to_date: Optional[date] = None


class RentPaymentSearch(BaseModel):
    tenant: str
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    show_subtotal: bool = False
    # description: str | None = None
    # price: float
    # tax: float | None = None
