"""
The main app is defined in this file.
"""
from fastapi import FastAPI, APIRouter, HTTPException
from config import db
from database.schemas import all_tasks
from database.models import Todo

app = FastAPI()
router = APIRouter()
collection = db["tasks"]

@router.get("/")
async def get_all_todos():
    """
    Route: gets all tasks
    """
    data = collection.find()
    return all_tasks(data)


@router.post("/")
async def create_task(new_task: Todo):
    """
    Route: create a task/todo
    """
    try:
        resp = collection.insert_one(dict(new_task))
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Some errors happened {e}")

app.include_router(router)
