"""
This script defines all operations.
"""

def get_task(todo):
    """ Returns the task detail of a given task """
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"],
        "status": todo["is_completed"]
    }


def get_tenant(tenant):
    """ Returns the tenant information of a given tenant """
    return {
        "_id": str(tenant["_id"]),
        "id": tenant["id"],
        "name": tenant["name"],
        "dob": tenant["dob"],
        "gender": tenant["gender"],
        "room": tenant["room"],
        "hb": tenant["hb"],
        "note": tenant["note"]
    }


def get_all_records(get_record_function, all_records):
    """ Returns all records """
    return [get_record_function(record) for record in all_records]
