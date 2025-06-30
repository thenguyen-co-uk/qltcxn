"""
Define the utilities and helpers
"""
from datetime import date, datetime, timedelta
from dateutil import rrule
from database.models import Income, IncomeEnum


def weeks_between(start_date, end_date):
    """
    Calculates the amount weeks between start_date and end_date.
    """
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()


def start_end_week(given_date):
    """
    Calculates the start and end date of the week by given_date.
    given_date: 2025-06-28 or a datetime.date object
    """
    if not given_date or given_date is None:
        today = date.today()
    elif isinstance(given_date, date):
        today = given_date
    else:
        today = datetime.strptime(given_date, '%Y-%m-%d').date()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def income_categories():
    """
    Returns a list of Income categories/types.
    """
    categories = []
    for k, v in IncomeEnum.__members__.items():
        categories.append({"name": v.value, "id": k})
    return categories


def reconcile_income_dates(income: Income):
    """ Reconciles the these date fields of the income
    The type of the dates sent from the client is datetime.date where the
    type of the ones on the server side (e.g., pydantic) is datetime.datetime
    """
    t = income.arrived_date
    income.arrived_date = datetime(t.year, t.month, t.day, 0, 0, 0)
    if income.category in ['Housing Benefit', 'Standing Order']:
        t = income.from_date
        income.from_date = datetime(t.year, t.month, t.day, 0, 0, 0)
        t = income.to_date
        income.to_date = datetime(t.year, t.month, t.day, 0, 0, 0)
    else:
        income.from_date = None
        income.to_date = None

    return income