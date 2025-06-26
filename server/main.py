"""
The main app is defined in this file.
"""
import json
from datetime import datetime, date
from pathlib import Path

from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config import db
from database.schemas import get_all_records, get_rent, get_task, get_tenant
from database.models import Rent, Tenant, Todo

app = FastAPI()
router = APIRouter()
col_tasks = db["tasks"]
col_tenants = db["tenant"]
col_rents = db["rent"]
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


@router.get("/tenants/list", response_class=HTMLResponse)
async def list_all_tenants(request: Request):
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


@router.get("/rent/{id}", response_class=HTMLResponse)
async def read_rent(request: Request, id: str):
    """Route: read a rent from the database"""
    rent = col_rents.find_one({"_id": ObjectId(id)})
    rent = get_rent(rent)
    tenants = get_all_records(get_tenant, col_tenants.find())
    return templates.TemplateResponse(
        "rent.html",
        {"request": request, "id": id, "rent": rent, "tenants": tenants}
    )


@router.get("/tenant/{id}", response_class=HTMLResponse)
async def read_tenant(request: Request, id: str):
    """Route: display a tenant"""
    tenant = col_tenants.find_one({"id": id})
    # tenant["dob"] = tenant["dob"].strftime("%Y-%m-%d")
    tenant = get_tenant(tenant)
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

@router.put("/rent/update/{rent_object_id}")
async def update_rent(rent_object_id: str, rent: Rent):
    """Route: update a given rent"""
    dt = rent.week_commence
    rent.week_commence = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    dt = rent.rent_due
    rent.rent_due = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    dt = rent.payment_date
    rent.payment_date = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    result = col_rents.update_one(
        {"_id": ObjectId(rent_object_id)},
        {"$set": dict(rent)}, upsert=False
    )

    return json.dumps({
        "status_code": 200,
        "acknowledged": result.acknowledged,
        "matched_count": result.matched_count
    })


@router.get("/rents")
async def get_all_rents():
    """Route: gets all rents"""
    data = col_rents.find()
    return get_all_records(get_rent, data)


@router.get("/rent/{id}")
async def retrieve_rent(id: str):
    """Route: retrieve a rent"""
    return {"message": f"rent {id}"}


@router.get("/rents/list", response_class=HTMLResponse)
async def list_all_rents(request: Request):
    """Route: show all rents"""
    data = get_all_records(get_rent, col_rents.find())
    return templates.TemplateResponse("rent-list.html",
                                      {"request": request, "data": data})


@router.post("/rent/add")
async def add_rent(new_rent: Rent):
    """Route: add a rent"""
    try:
        d = dict(new_rent)
        date_format = '%Y-%m-%d'
        d["week_commence"] = datetime.strptime(str(d["week_commence"]), date_format)
        d["rent_due"] = datetime.strptime(str(d["rent_due"]), date_format)
        d["payment_date"] = datetime.strptime(str(d["payment_date"]), date_format)
        resp = col_rents.insert_one(d)
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        return HTTPException(status_code=500,
                             detail=f"Some errors happened {e}")


@router.get("/add/rent", response_class=HTMLResponse)
async def render_add_rent(request: Request):
    """Route: render the form to add a rent"""
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    rent = Rent(tenant_id="",
                week_commence=date(year, month, day),
                rent_due=date(year, month, day),
                payment_date=date(year, month, day),
                standing_order=0.0,
                extra=0.0, notes="")
    rent.week_commence = rent.week_commence.strftime("%d/%m/%Y")
    rent.rent_due = rent.rent_due.strftime("%d/%m/%Y")
    rent.payment_date = rent.payment_date.strftime("%d/%m/%Y")
    tenants = get_all_records(get_tenant, col_tenants.find())
    return templates.TemplateResponse("rent-add.html",
        {"request": request, "rent": rent, "action": "add", "tenants": tenants})


@router.get("/add/tenant", response_class=HTMLResponse)
async def render_add_tenant(request: Request):
    """Route: render the form to add a tenant"""
    return templates.TemplateResponse("tenant-add.html",
                                      {"request": request, "name": "Tung"})

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request, "name": "Tung"})

app.include_router(router)
