"""
The main app is defined in this file.
"""
from datetime import datetime

from fastapi import FastAPI, APIRouter, HTTPException
from config import db
from database.schemas import get_all_records, get_task, get_tenant
from database.models import Tenant, Todo

app = FastAPI()
router = APIRouter()
col_tasks = db["tasks"]
col_tenants = db["tenant"]

@router.get("/tasks")
async def get_all_todos():
    """Route: gets all tasks"""
    data = col_tasks.find()
    return get_all_records(get_task, data)


@router.post("/create-task")
async def create_task(new_task: Todo):
    """Route: create a task"""
    try:
        resp = col_tasks.insert_one(dict(new_task))
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        return HTTPException(status_code=500,
                             detail=f"Some errors happened {e}")


@router.get("/tenants")
async def get_all_tenants():
    """Route: gets all tenants"""
    data = col_tenants.find()
    return get_all_records(get_tenant, data)


@router.post("/add-tenant")
async def add_tenant(new_tenant: Tenant):
    """Route: add a tenant"""
    try:
        d = dict(new_tenant)
        date_format = '%Y-%m-%d'
        d["dob"] = datetime.strptime(str(d["dob"]), date_format)
        resp = col_tenants.insert_one(d)
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        return HTTPException(status_code=500,
                             detail=f"Some errors happened {e}")

app.include_router(router)
