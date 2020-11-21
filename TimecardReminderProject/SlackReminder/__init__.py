import logging
import azure.functions as func
import os
import requests
from bs4 import BeautifulSoup, element
from datetime import datetime, timezone, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_html(url: str):
    """
    Return the HTML code for a given URL

    url - The URL to fetch HTML from
    """

    payload = {}
    headers = {}
    response = requests.request("GET", url, headers = headers, data = payload)
    return response.text.encode("utf8")


def get_semi_monthly_table(soup: BeautifulSoup):
    """
    Return the table tag pertaining to the Semi-Monthly Payroll Schedule

    soup - BeautifulSoup HTML parser object
    """

    # Find tag that resembles <table summary="Semi-monthly Payroll Schedule">
    table = soup.find_all("table", {"summary" : "Semi-monthly Payroll Schedule"}, limit = 1)
    return table


def get_monthly_table(soup: BeautifulSoup):
    """
    Return the table tag pertaining to the Monthly Payroll Schedule

    soup - BeautifulSoup HTML parser object
    """

    # Find tag that resembles <table summary="Monthly Payroll Schedule">
    table = soup.find_all("table", {"summary" : "Monthly Payroll Schedule"}, limit = 1)
    return table


def get_semi_monthly_due_dates(table: element.ResultSet):
    """
    Return a list of all the due dates from the semi-monthly table

    table - the semi_monthly_table BeautifulSoup ResultSet
    """

    if len(table) != 1:
        return []
    else:
        # Find tag that resembles <strong>
        strongs = table[0].find_all("strong")
        due_dates = []
        for strong in strongs:
            strong_contents = strong.contents[0] # Should expect date to be in format: mm/dd/yyyy
            try:
                datetime_object = datetime.strptime(strong_contents, "%m/%d/%Y")
                due_dates.append(datetime_object)
            except:
                # strong tag did not contain a date, so skip
                continue

        return due_dates


def get_monthly_due_dates(table: element.ResultSet):
    """
    Return a list of all the due dates from the monthly table

    table - the monthly_table BeautifulSoup ResultSet
    """

    if len(table) != 1:
        return []
    else:
        # Find tag that resembles <td style="font-weight: bold; color: red;">
        tds = table[0].find_all("td", {"style" : "font-weight: bold; color: #ad0901;"})
        due_dates = []
        for td in tds:
            td_contents = td.contents[0] # Should expect date to be in format: mm/dd/yyyy
            try:
                datetime_object = datetime.strptime(td_contents, "%m/%d/%Y")
                due_dates.append(datetime_object)
            except:
                # td tag did not contain a date, so skip
                continue

        return due_dates


def remove_past_due_dates(dates):
    """
    Removes all the dates in dates that are in the past

    dates - list of datetime objects that represent all the timecard due dates
    """

    todays_date = datetime.today()
    new_dates = []
    for date in dates:
        # skip over all dates that are in the past
        if date < todays_date:
            continue
        else:
            new_dates.append(date)

    return new_dates


def is_same_date(date1: datetime, date2: datetime):
    """
    Return True is date1 is equal to date2

    date1 - A datetime object
    date2 - A datetime object
    """

    return date1.year == date2.year and date1.month == date2.month and date1.day == date2.day


def should_notify(upcoming_due_date):
    """
    Given a list of dates, determine if a notification should be sent

    upcoming_due_date - The date representing the next (upcoming) timecard due date

    Return: (True or False for a notification, days before due)
            If False, days before due will be -1
    """

    todays_date = datetime.today()
    one_day = timedelta(
        weeks = 0,
        days = 1,
        hours = 0,
        minutes = 0,
        seconds = 0,
        milliseconds = 0,
        microseconds = 0
    )
    two_day = timedelta(
        weeks = 0,
        days = 2,
        hours = 0,
        minutes = 0,
        seconds = 0,
        milliseconds = 0,
        microseconds = 0
    )

    # Timecard is due same day
    if is_same_date(upcoming_due_date, todays_date):
        return True, 0

    # Timecard is due tomorrow
    if is_same_date(upcoming_due_date, todays_date + one_day):
        return True, 1

    # Timecard is due two days from now
    if is_same_date(upcoming_due_date, todays_date + two_day):
        return True, 2

    return False, -1


def send_reminder_notification(due_date: datetime, num_days_until_due: int):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))

    try:
        # -1 would indicate a notification shouldn't be sent (this case should never occur here)
        if num_days_until_due <= -1:
            return

        message = ""
        if num_days_until_due > 1:
            message = f"Timecards are due in {num_days_until_due} days! *{due_date.date().month}/{due_date.date().day}/{due_date.date().year}*"
        elif num_days_until_due == 1:
            message = f"Timecards are due tomorrow! *{due_date.date().month}/{due_date.date().day}/{due_date.date().year}*"
        elif num_days_until_due == 0:
            message = f"Timecards are due *TODAY! {due_date.date().month}/{due_date.date().day}/{due_date.date().year}*"

        response = client.chat_postMessage(channel="#bot-testing", text=message)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
        logging.error(f"Got an error: {e.response['error']}")


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    url = "https://www.utrgv.edu/financial-services-comptroller/departments/payroll-and-tax-compliance/payroll-schedules-and-deadlines/index.htm"
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # Get HTML tables
    semi_monthly_table = get_semi_monthly_table(soup)
    monthly_table = get_monthly_table(soup)

    # Extract due dates from tables
    semi_monthly_due_dates = remove_past_due_dates(get_semi_monthly_due_dates(semi_monthly_table))
    monthly_due_dates = remove_past_due_dates(get_monthly_due_dates(monthly_table))

    # Get the upcoming due date
    semi_monthly_upcoming_due_date = semi_monthly_due_dates[0]
    monthly_upcoming_due_date = monthly_due_dates[0]

    # Determine if to send notification
    semi_monthly_should_notify, semi_monthly_due_when = should_notify(semi_monthly_upcoming_due_date)
    monthly_should_notify, monthly_due_when = should_notify(monthly_upcoming_due_date)

    # Send reminder notifications if it was determined
    if semi_monthly_should_notify:
        send_reminder_notification(semi_monthly_upcoming_due_date, semi_monthly_due_when)

    if monthly_should_notify:
        send_reminder_notification(monthly_upcoming_due_date, monthly_due_when)

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
