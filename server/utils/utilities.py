"""
Define the utilities and helpers
"""
from dateutil import rrule

def weeks_between(start_date, end_date):
    """
    Calculates the amount weeks between start_date and end_date.
    """
    weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date, until=end_date)
    return weeks.count()