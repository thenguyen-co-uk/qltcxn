"""
This script defines all operations.
"""
import collections
from datetime import datetime, timedelta

from database.models import Income, IncomeEnum, Rent, Room, Tenant
from utils.utilities import start_end_week


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
    data["total_balance"] = "{:,.2f}".format(total_balance)
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
        "arrived_date": income["arrived_date"].date()
    }
    if income["from_date"] is not None:
        data["from_date"] = income["from_date"].date()
    if income["to_date"] is not None:
        data["to_date"] = income["to_date"].date()

    return data


def get_all_records(get_record_function, all_records):
    """ Returns all records """
    return [get_record_function(record) for record in all_records]


def calculate_subtotal_incomes(incomes):
    """ Calculates the subtotal for given incomes """
    result = {}
    for income in incomes:
        if income["category"] not in result:
            result[income["category"]] = [income]
        else:
            cate = result[income["category"]]
            cate.append(income)
    od = collections.OrderedDict(sorted(result.items()))
    return od


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
