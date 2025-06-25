"""
This script defines all operations.
"""
from database.models import Rent, Tenant


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
        "id": tenant["id"],
        "name": tenant["name"],
        "dob": tenant["dob"],
        "gender": tenant["gender"],
        "room": tenant["room"],
        "hb": tenant["hb"],
        "notes": tenant["notes"]
    }


def get_rent(rent: Rent):
    """ Returns the rent information of a given tenant """
    return {
        "_id": str(rent["_id"]),
        "tenant_id": rent["tenant_id"],
        "week_commence": rent["week_commence"],
        "rent_due": rent["rent_due"],
        "payment_date": rent["payment_date"],
        "standing_order": rent["standing_order"],
        "extra": rent["extra"]
    }


def get_all_records(get_record_function, all_records):
    """ Returns all records """
    return [get_record_function(record) for record in all_records]
