"""
The main app is defined in this file.
"""
from datetime import date, datetime, timedelta
from pathlib import Path

from bson import ObjectId
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import db
from database.models import Income, IncomeEnum, Rent, RentPaymentSearch, Room, \
    Tenant, Todo
from database.schemas import calculate_subtotal_incomes, get_all_records, \
    get_income, get_rent, get_room, \
    get_task, \
    get_tenant
from utils.utilities import income_categories, start_end_week, weeks_between

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
    if income.category in ['Housing Benefit', 'Standing Order']:
        t = income.from_date
        income.from_date = datetime(t.year, t.month, t.day, 0, 0, 0)
    else:
        income.from_date = None
    if income.category in ['Housing Benefit', 'Standing Order']:
        t = income.to_date
        income.to_date = datetime(t.year, t.month, t.day, 0, 0, 0)
    else:
        income.to_date = None
    return income


@router.get("/categories", response_class=HTMLResponse)
async def categories(req: Request):
    """ Renders the categories page """
    ctx = {"request": req}
    return templates.TemplateResponse("categories.html", ctx)


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
async def delete_tenant(req: Request, _id: str):
    """Route: delete a tenant"""
    result = col_tenants.find_one_and_delete({"_id": ObjectId(_id)})
    return {
        "request": req,
        "status_code": 200,
        "_id": _id,
        "message": f"tenant {_id} deleted"
    }


@router.get("/income/{id}", response_class=HTMLResponse)
async def read_income(req: Request, id: str):
    """Route: read an income"""
    income = col_incomes.find_one({"_id": ObjectId(id)})
    income = get_income(income)
    _categories = income_categories()
    r = [item for item in _categories if item["name"] == income["category"]]
    ctx = {
        "request": req,
        "id": id,
        "income": income,
        "action": "read",
        "categories": _categories,
        "category": str(r[0]["name"])
    }
    return templates.TemplateResponse("income.html", ctx)


@router.get("/rent/{id}", response_class=HTMLResponse)
async def read_rent(req: Request, id: str):
    """Route: read a rent from the database"""
    rent = col_rents.find_one({"_id": ObjectId(id)})
    rent = get_rent(rent)
    tenants = get_all_records(get_tenant, col_tenants.find())
    ctx = {
        "request": req,
        "id": id,
        "rent": rent,
        "tenants": tenants,
        "action": "read"
    }
    return templates.TemplateResponse("rent.html", ctx)


@router.get("/room/{id}", response_class=HTMLResponse)
async def read_room(req: Request, id: str):
    """Route: read a room from the database"""
    room = col_rooms.find_one({"_id": ObjectId(id)})
    room = get_room(room)
    ctx = {"request": req, "id": id, "room": room}
    return templates.TemplateResponse("room.html", ctx)

@router.get("/tenant/{id}", response_class=HTMLResponse)
async def read_tenant(req: Request, id: str):
    """Route: display a tenant"""
    tenant = col_tenants.find_one({"id": id})
    tenant = get_tenant(tenant)
    ctx = {"request": req, "id": id, "tenant": tenant}
    return templates.TemplateResponse("tenant.html", ctx)


@router.get("/reports", response_class=HTMLResponse)
async def reports(req: Request):
    """Route: render the reports page"""
    ctx = {"request": req}
    return templates.TemplateResponse("reports.html", ctx)


@router.get("/reports/rent-payment", response_class=HTMLResponse)
async def reports_rent_payment(req: Request):
    """Route: render the reports page for the incomes"""
    tenants = get_all_records(get_tenant, col_tenants.find())

    ctx = {"request": req, "tenants": tenants}
    return templates.TemplateResponse("reports-rent-payment.html", ctx)


def calculate_total_groups(groups):
    """Function: calculate total groups"""
    result = {}
    for k, v in groups.items():
        total = 0
        for income in v:
            total += income["amount"]
        result[k] = "{:,.2f}".format(total)
    return result


def calculate_total_rents(rents):
    """Function: render the reports page for the incomes"""
    result = {
        "rent_due": 0,
        "services": 0,
        "utilities": 0,
        "meals": 0,
        "extra": 0,
        "total": 0
    }
    for rent in rents:
        result["rent_due"] += rent["rent_due"]
        result["services"] += rent["services"]
        result["utilities"] += rent["utilities"]
        result["meals"] += rent["meals"]
        result["extra"] += rent["extra"]
        result["total"] += rent["rent_due"]+rent["services"]
        result["total"] += rent["utilities"]+rent["meals"]+rent["extra"]

    return result


def filter_incomes_by_dates(incomes, from_date, to_date):
    """Function: filter incomes by dates"""
    begin_date_of_from, end_date_of_from = start_end_week(from_date)
    begin_date_of_to, end_date_of_to = start_end_week(to_date)
    start = begin_date_of_from
    weeks_included = []
    while start <= end_date_of_to:
        weeks_included.append(start)
        start += timedelta(days=7)
    # print(weeks_included)
    filtered_incomes = []
    for income in incomes:
        ic_from_date = income["from_date"].date()
        ic_to_date = income["to_date"].date()
        if ic_from_date >= begin_date_of_from and ic_to_date <= end_date_of_to:
            filtered_incomes.append(income)
        elif (ic_from_date.month != ic_to_date.month
            and income["category"] == IncomeEnum.HOUSING_BENEFIT.value
            and ((begin_date_of_from <= ic_to_date <= end_date_of_to)
                 or (begin_date_of_from <= ic_from_date <= end_date_of_to))):
            start = ic_from_date
            weeks = []
            while start <= ic_to_date:
                weeks.append(start)
                start += timedelta(days=7)
            # print(weeks)
            t = 0
            for week in weeks:
                if week in weeks_included:
                    t += 1
            # print(t)
            amount = income["amount"]/len(weeks)*t
            income["amount"] = amount
            filtered_incomes.append(income)
    return filtered_incomes


def filter_rents_by_dates(rents, from_date, to_date):
    """ Filter the rents by tenants. """
    begin_date_of_from, end_date_of_from = start_end_week(from_date)
    begin_date_of_to, end_date_of_to = start_end_week(to_date)
    filtered_rents = []
    for rent in rents:
        if begin_date_of_from <= rent["week_commence"].date() <= end_date_of_to:
            filtered_rents.append(rent)
    return filtered_rents


@router.post("/reports/rent-payment/search", response_class=HTMLResponse)
async def reports_rent_payment_search(item: RentPaymentSearch, req: Request):
    """Route: search or filter for the incomes"""
    tenant = col_tenants.find_one({"_id": ObjectId(item.tenant)})
    rents = col_rents.find({"tenant_id": tenant["id"]})
    rents = filter_rents_by_dates(rents, item.from_date, item.to_date)
    total_rents = calculate_total_rents(rents)
    cursor = col_incomes.find({"for_tenant": tenant["id"]})
    incomes = list(cursor)
    incomes = filter_incomes_by_dates(incomes, item.from_date, item.to_date)
    groups = None
    total_groups = None
    if item.show_subtotal:
        groups = calculate_subtotal_incomes(incomes)
        total_groups = calculate_total_groups(groups)
    message = "The results are being processed..."
    total_amount = sum([income["amount"] for income in incomes])
    ctx = {
        "request": req,
        "message": message,
        "tenant_id": item.tenant,
        "incomes": incomes,
        "total_amount": total_amount,
        "show_subtotal": item.show_subtotal,
        "groups": groups,
        "total_groups": total_groups,
        "rents": rents,
        "total_rents": total_rents
    }
    return templates.TemplateResponse("_reports-rent-payment.html", ctx)


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
async def list_all_incomes(req: Request):
    """Route: get incomes list"""
    data = get_all_records(get_income, col_incomes.find())
    ctx = {
        "request": req,
        "incomes": data
    }
    return templates.TemplateResponse("income-list.html", ctx)


@router.get("/rents/list", response_class=HTMLResponse)
async def list_all_rents(req: Request):
    """Route: show all rents"""
    data = get_all_records(get_rent, col_rents.find())
    ctx = {"request": req, "rents": data}
    return templates.TemplateResponse("rent-list.html", ctx)


@router.get("/rooms/list", response_class=HTMLResponse)
async def list_all_rooms(req: Request):
    """Route: list all rooms"""
    rooms = get_all_records(get_room, col_rooms.find())
    ctx = {"request": req, "rooms": rooms}
    return templates.TemplateResponse("room-list.html", ctx)


@router.get("/tenants/list", response_class=HTMLResponse)
async def list_all_tenants(req: Request):
    """Route: show all tenants"""
    data = get_all_records(get_tenant, col_tenants.find())
    ctx = {"request": req, "data": data}
    return templates.TemplateResponse("tenant-list.html", ctx)


@router.post("/income/add")
async def add_income(new_income: Income):
    """Route: add an income"""
    try:
        d = dict(new_income)
        df = '%Y-%m-%d'
        d["arrived_date"] = datetime.strptime(str(d["arrived_date"]), df)
        if d["category"] not in ['Housing Benefit', 'Standing Order']:
            d["from_date"] = None
            d["to_date"] = None
        else:
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
async def render_add_income(req: Request):
    """Route: render the form to add an income"""
    dt_now = datetime.now()
    d_now = dt_now.date()
    income = Income(description="", amount=0, for_tenant="",
                    category=IncomeEnum.STANDING_ORDER, arrived_date=d_now,
                    from_date=d_now, to_date=d_now)
    _categories = income_categories()
    ctx = {
        "request": req,
        "income": income,
        "action": "add",
        "categories": _categories
    }
    return templates.TemplateResponse("income-add.html", ctx)


@router.get("/add/rent", response_class=HTMLResponse)
async def render_add_rent(req: Request):
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
    ctx = {
        "request": req, "rent": rent, "action": "add", "tenants": tenants
    }
    return templates.TemplateResponse("rent-add.html", ctx)


@router.get("/add/room", response_class=HTMLResponse)
async def render_add_room(req: Request):
    """Route: render the form to add a room"""
    room = Room(id="", name="room", description="", area="")
    ctx = {
        "request": req, "room": room, "action": "add"
    }
    return templates.TemplateResponse("room-add.html", ctx)

@router.get("/add/tenant", response_class=HTMLResponse)
async def render_add_tenant(req: Request):
    """Route: render the form to add a tenant"""
    dt_now = datetime.now()
    dob = dt_now.date()
    tenant = Tenant(id="", name="", dob=dob, gender="male", room="", hb=True,
                    notes="", creation=0, modification=0)
    ctx_dict = {
        "request": req, "name": "Tung", "tenant": tenant, "action": "add"
    }
    return templates.TemplateResponse("tenant-add.html", ctx_dict)

@router.get("/", response_class=HTMLResponse)
async def root(req: Request):
    d1 = datetime.strptime("2025-05-19", '%Y-%m-%d')
    d2 = datetime.strptime("2025-06-15", '%Y-%m-%d')
    diff = d2 - d1
    weeks = weeks_between(d1, d2)
    data = f'days : {diff.days + 1} - weeks : {(diff.days + 1)//7} - w: {weeks}'
    s, e = start_end_week("2025-02-28")
    data += f"s: {s}, e: {e}"
    ctx = {"request": req, "name": "Tung", "data": data}
    return templates.TemplateResponse("index.html", ctx)

app.include_router(router)
