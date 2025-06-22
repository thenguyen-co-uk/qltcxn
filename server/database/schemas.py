"""
This script defines all operations.
"""

def individual_data(todo):
    """
    Returns the task of a given todo
    """
    return {
        "id": str(todo["_id"]),
        "title": todo["title"],
        "description": todo["description"],
        "status": todo["is_completed"]
    }


def all_tasks(todos):
    """
    Returns all tasks, aka. all todos
    """
    return [individual_data(todo) for todo in todos]
