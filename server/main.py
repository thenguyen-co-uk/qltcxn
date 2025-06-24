"""
The main app is defined in this file.
"""
import json
from datetime import datetime
from pathlib import Path

from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config import db
from database.schemas import get_all_records, get_task, get_tenant
from database.models import Tenant, Todo

app = FastAPI()
router = APIRouter()
col_tasks = db["tasks"]
col_tenants = db["tenant"]
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


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


@router.get("/tenants/show", response_class=HTMLResponse)
async def show_all_tenants(request: Request):
    """Route: show all tenants"""
    data = get_all_records(get_tenant, col_tenants.find())
    return templates.TemplateResponse("tenant-list.html",
                                      {"request": request, "data": data})


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


@router.get("/tenant/{id}", response_class=HTMLResponse)
async def read_tenant(request: Request, id: str):
    """Route: display a tenant"""
    tenant = col_tenants.find_one({"id": id})
    tenant["dob"] = tenant["dob"].strftime("%Y-%m-%d")
    return templates.TemplateResponse(
        "tenant.html", {"request": request, "id": id, "tenant": tenant}
    )


@router.put("/tenant/update/{tenant_object_id}")
async def update_tenant(tenant_object_id: str, tenant: Tenant):
    """Route: update a given tenant"""
    dob = tenant.dob
    tenant.dob = datetime(dob.year, dob.month, dob.day, 0, 0, 0)
    tenant.creation = int(tenant.creation)
    tenant.modification = int(tenant.modification)
    result = col_tenants.update_one(
        {"_id": ObjectId(tenant_object_id)},
        {"$set": dict(tenant)}, upsert=False
    )

    return json.dumps({
        "status_code": 200,
        "acknowledged": result.acknowledged,
        "matched_count": result.matched_count
    })

    """ return templates.TemplateResponse(
        "tenant.html", {"request": request, "id": id, "tenant": tenant}
    ) """


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request, "name": "Tung"})

app.include_router(router)
