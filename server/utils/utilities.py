"""
Define the utilities and helpers
"""
from dateutil import rrule

from database.models import IncomeEnum


def weeks_between(start_date, end_date):
    """
    Calculates the amount weeks between start_date and end_date.
    """
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()


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
