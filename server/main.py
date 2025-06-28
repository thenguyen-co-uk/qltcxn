"""
The main app is defined in this file.
"""
from datetime import datetime, date
from pathlib import Path
from urllib import request

from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config import db
from database.schemas import get_all_records, get_income, get_rent, get_room, \
    get_task, \
    get_tenant
from database.models import Income, IncomeEnum, Rent, Room, Tenant, Todo

app = FastAPI()
router = APIRouter()
col_tasks = db["tasks"]
col_tenants = db["tenant"]
col_rents = db["rent"]
col_rooms = db["room"]
col_incomes = db["income"]
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def reconcile(income: Income):
    """
    Reconciles the dates of the income
    """
    t = income.arrived_date
    income.arrived_date = datetime(t.year, t.month, t.day, 0, 0, 0)
    t = income.from_date
    income.from_date = datetime(t.year, t.month, t.day, 0, 0, 0)
    t = income.to_date
    income.to_date = datetime(t.year, t.month, t.day, 0, 0, 0)
    return income


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


@router.delete("/tenant/delete/{_id}")
async def delete_tenant(request: Request, _id: str):
    """Route: delete a tenant"""
    result = col_tenants.find_one_and_delete({"_id": ObjectId(_id)})
    return {
        "status_code": 200,
        "_id": _id,
        "message": f"tenant {_id} deleted"
    }


@router.get("/income/{id}", response_class=HTMLResponse)
async def read_income(request: Request, id: str):
    """Route: read an income"""
    income = col_incomes.find_one({"_id": ObjectId(id)})
    income = get_income(income)
    ctx = {
        "request": request,
        "id": id,
        "income": income,
        "action": "read"
    }
    return templates.TemplateResponse("income.html", ctx)


@router.get("/rent/{id}", response_class=HTMLResponse)
async def read_rent(request: Request, id: str):
    """Route: read a rent from the database"""
    rent = col_rents.find_one({"_id": ObjectId(id)})
    rent = get_rent(rent)
    tenants = get_all_records(get_tenant, col_tenants.find())
    ctx = {
        "request": request,
        "id": id,
        "rent": rent,
        "tenants": tenants,
        "action": "read"
    }
    return templates.TemplateResponse("rent.html", ctx)


@router.get("/room/{id}", response_class=HTMLResponse)
async def read_room(request: Request, id: str):
    """Route: read a room from the database"""
    room = col_rooms.find_one({"_id": ObjectId(id)})
    room = get_room(room)
    ctx = {"request": request, "id": id, "room": room}
    return templates.TemplateResponse("room.html", ctx)

@router.get("/tenant/{id}", response_class=HTMLResponse)
async def read_tenant(request: Request, id: str):
    """Route: display a tenant"""
    tenant = col_tenants.find_one({"id": id})
    # tenant["dob"] = tenant["dob"].strftime("%Y-%m-%d")
    tenant = get_tenant(tenant)
    return templates.TemplateResponse(
        "tenant.html", {"request": request, "id": id, "tenant": tenant}
    )


@router.put("/income/update/{income_object_id}")
async def update_income(income_object_id: str, income: Income):
    """Route: update a given income"""
    income = reconcile(income)
    result = col_incomes.update_one(
        {"_id": ObjectId(income_object_id)},
        {"$set": dict(income)}, upsert=False
    )

    return {
        "status_code": 200,
        "message": f"tenant {income_object_id} updated",
        "acknowledged": result.acknowledged,
        "matched_count": result.matched_count
    }


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

    return {
        "status_code": 200,
        "message": f"tenant {tenant_object_id} updated",
        "acknowledged": result.acknowledged,
        "matched_count": result.matched_count
    }


@router.put("/rent/update/{rent_object_id}")
async def update_rent(rent_object_id: str, rent: Rent):
    """Route: update a given rent"""
    dt = rent.week_commence
    # because the view shows and the datetime picker is set dd/mm/yyyy
    rent.week_commence = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    result = col_rents.update_one(
        {"_id": ObjectId(rent_object_id)},
        {"$set": dict(rent)}, upsert=False
    )

    return {
        "status_code": 200,
        "message": f"rent {rent_object_id} updated",
        "acknowledged": result.acknowledged,
        "matched_count": result.matched_count
    }


@router.put("/room/update/{room_object_id}")
async def update_room(room_object_id: str, room: Room):
    """Route: update a given room"""
    result = col_rooms.update_one(
        {"_id": ObjectId(room_object_id)},
        {"$set": dict(room)}, upsert=False
    )

    return {
        "status_code": 200,
        "message": f"room {room_object_id} updated",
        "acknowledged": result.acknowledged,
        "matched_count": result.matched_count
    }


@router.get("/rents")
async def get_all_rents():
    """Route: gets all rents"""
    data = col_rents.find()
    return get_all_records(get_rent, data)


@router.get("/rent/{id}")
async def retrieve_rent(id: str):
    """Route: retrieve a rent"""
    return {"message": f"rent {id}"}


@router.get("/incomes/list", response_class=HTMLResponse)
async def list_all_incomes(request: Request):
    """Route: get incomes list"""
    data = get_all_records(get_income, col_incomes.find())
    ctx = {
        "request": request,
        "incomes": data
    }
    return templates.TemplateResponse("income-list.html", ctx)


@router.get("/rents/list", response_class=HTMLResponse)
async def list_all_rents(request: Request):
    """Route: show all rents"""
    data = get_all_records(get_rent, col_rents.find())
    ctx = {"request": request, "rents": data}
    return templates.TemplateResponse("rent-list.html", ctx)


@router.get("/rooms/list", response_class=HTMLResponse)
async def list_all_rooms(request: Request):
    """Route: list all rooms"""
    rooms = get_all_records(get_room, col_rooms.find())
    ctx = {"request": request, "rooms": rooms}
    return templates.TemplateResponse("room-list.html", ctx)


@router.get("/tenants/list", response_class=HTMLResponse)
async def list_all_tenants(request: Request):
    """Route: show all tenants"""
    data = get_all_records(get_tenant, col_tenants.find())
    ctx = {"request": request, "data": data}
    return templates.TemplateResponse("tenant-list.html", ctx)


@router.post("/income/add")
async def add_income(new_income: Income):
    """Route: add an income"""
    try:
        d = dict(new_income)
        # new_income["category"] = IncomeEnum.STANDING_ORDER
        df = '%Y-%m-%d'
        d["arrived_date"] = datetime.strptime(str(d["arrived_date"]), df)
        d["from_date"] = datetime.strptime(str(d["from_date"]), df)
        d["to_date"] = datetime.strptime(str(d["to_date"]), df)
        resp = col_incomes.insert_one(d)
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        return HTTPException(status_code=500,
                             detail=f"Some errors happened {e}")


@router.post("/room/add")
async def add_room(new_room: Room):
    """Route: add a room"""
    try:
        d = dict(new_room)
        resp = col_rooms.insert_one(d)
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        return HTTPException(status_code=500,
                             detail=f"Some errors happened {e}")

@router.post("/rent/add")
async def add_rent(new_rent: Rent):
    """Route: add a rent"""
    try:
        d = dict(new_rent)
        df = '%Y-%m-%d'
        d["week_commence"] = datetime.strptime(str(d["week_commence"]), df)
        resp = col_rents.insert_one(d)
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        return HTTPException(status_code=500,
                             detail=f"Some errors happened {e}")


@router.post("/tenant/add")
async def add_tenant(new_tenant: Tenant):
    """Route: add a tenant"""
    try:
        d = dict(new_tenant)
        df = '%Y-%m-%d'
        d["dob"] = datetime.strptime(str(d["dob"]), df)
        resp = col_tenants.insert_one(d)
        return {"status_code": 200, "id": str(resp.inserted_id)}
    except Exception as e:
        return HTTPException(status_code=500,
                             detail=f"Some errors happened {e}")


@router.get("/add/income", response_class=HTMLResponse)
async def render_add_income(request: Request):
    """Route: render the form to add an income"""
    dt_now = datetime.now()
    d_now = dt_now.date()
    income = Income(id=0, description="", amount=0, for_tenant="LKPHUNG",
                    category=IncomeEnum.STANDING_ORDER, arrived_date=d_now,
                    from_date=d_now, to_date=d_now)
    ctx_dict = {"request": request, "income": income, "action": "add"}
    return templates.TemplateResponse("income-add.html", ctx_dict)


@router.get("/add/rent", response_class=HTMLResponse)
async def render_add_rent(request: Request):
    """Route: render the form to add a rent"""
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    rent = Rent(tenant_id="",
                week_commence=date(year, month, day),
                rent_due=0.0, services=0.0, utilities=0.0, meals=0.0,
                extra=0.0, notes="")
    rent.week_commence = rent.week_commence.strftime("%d/%m/%Y")
    tenants = get_all_records(get_tenant, col_tenants.find())
    return templates.TemplateResponse("rent-add.html",
        {"request": request, "rent": rent, "action": "add", "tenants": tenants})


@router.get("/add/room", response_class=HTMLResponse)
async def render_add_room(request: Request):
    """Route: render the form to add a room"""
    room = Room(id="", name="room", description="", area="")
    ctx = {
        "request": request,
        "room": room,
        "action": "add"
    }
    return templates.TemplateResponse("room-add.html", ctx)

@router.get("/add/tenant", response_class=HTMLResponse)
async def render_add_tenant(request: Request):
    """Route: render the form to add a tenant"""
    dt_now = datetime.now()
    dob = dt_now.date()
    tenant = Tenant(id="", name="", dob=dob, gender="male", room="", hb=True,
                    notes="", creation=0, modification=0)
    ctx_dict = {"request": request, "name": "Tung", "tenant": tenant, "action": "add"}
    return templates.TemplateResponse("tenant-add.html", ctx_dict)

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request, "name": "Tung"})

app.include_router(router)
