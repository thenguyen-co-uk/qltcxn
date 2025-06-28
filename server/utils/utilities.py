"""
Define the utilities and helpers
"""
from datetime import date, datetime, timedelta
from dateutil import rrule
from database.models import IncomeEnum


def weeks_between(start_date, end_date):
    """
    Calculates the amount weeks between start_date and end_date.
    """
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()


def start_end_week(given_date):
    """
    Calculates the start and end date of the week by given_date.
    given_date: 2025-06-28
    """
    if not given_date or given_date is None:
        today = date.today()
    else:
        today = datetime.strptime(given_date, '%Y-%m-%d').date()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def income_categories():
    """
    Returns a list of Income categories.
    """
    categories = [
        {
            "name": IncomeEnum.STANDING_ORDER.value,
            "id": IncomeEnum.STANDING_ORDER
        },
        {
            "name": IncomeEnum.HOUSING_BENEFIT.value,
            "id": IncomeEnum.HOUSING_BENEFIT
        },
        {
            "name": IncomeEnum.REFUND.value,
            "id": IncomeEnum.REFUND
        }
    ]

    return categories
