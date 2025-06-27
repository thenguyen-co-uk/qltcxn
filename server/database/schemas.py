"""
This script defines all operations.
"""
from datetime import datetime

from database.models import Income, Rent, Room, Tenant


def get_task(todo):
    """ Returns the task detail of a given task """
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"],
        "status": todo["is_completed"]
    }


def get_tenant(tenant: Tenant):
    """ Returns the tenant information of a given tenant """
    return {
        "_id": str(tenant["_id"]),
        "name": tenant["name"],
        "dob": tenant["dob"].strftime("%d/%m/%Y"),
        "gender": tenant["gender"],
        "room": tenant["room"],
        "hb": tenant["hb"],
        "creation": datetime.fromtimestamp(tenant["creation"]),
        "modification": datetime.fromtimestamp(tenant["modification"]),
        "notes": tenant["notes"]
    }


def get_rent(rent: Rent):
    """ Returns the dict of a given rent information """
    data =  {
        "_id": str(rent["_id"]),
        "tenant_id": rent["tenant_id"],
        "week_commence": rent["week_commence"].strftime("%d/%m/%Y"),
        "rent_due": rent["rent_due"],
        "extra": rent["extra"]
    }
    total_balance = rent["rent_due"] + rent["extra"]
    if "services" in rent:
        data["services"] = rent["services"]
        total_balance += rent["services"]
    if "utilities" in rent:
        data["utilities"] = rent["utilities"]
        total_balance += rent["utilities"]
    if "meals" in rent:
        data["meals"] = rent["meals"]
        total_balance += rent["meals"]
    if "notes" in rent:
        data["notes"] = rent["notes"]
    data["total_balance"] = "{:.2f}".format(total_balance)
    return data


def get_room(room: Room):
    """ Returns the rooms information of a given room """
    data = {
        "_id": str(room["_id"]),
        "id": str(room["id"]),
        "name": room["name"],
        "description": room["description"],
        "area": room["area"],
    }

    return data


def get_income(income: Income):
    """ Returns the income information of a given income """
    data = {
        "_id": str(income["_id"]),
        "for_tenant": income["for_tenant"],
        "description": income["description"],
        "amount": income["amount"],
        "category": income["category"],
        "arrived_date": income["arrived_date"].date(),#.strftime("%d/%m/%Y"),
        "from_date": income["from_date"].date(),#.strftime("%d/%m/%Y"),
        "to_date": income["to_date"].date()#.strftime("%d/%m/%Y")
    }
    return data


def get_all_records(get_record_function, all_records):
    """ Returns all records """
    return [get_record_function(record) for record in all_records]
