#!/usr/bin/env python

import requests
from datetime import datetime
from bs4 import BeautifulSoup, element

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
        tds = table[0].find_all("td", {"style" : "font-weight: bold; color: red;"})
        due_dates = []
        for td in tds:
            td_contents = td.contents[0] # Should expect date to be in format: mm/dd/yyyy
            try:
                datetime_object = datetime.strptime(td_contents, "%m/%d/%Y")
                due_dates.append(datetime_object)
            except:
                # strong tag did not contain a date, so skip
                continue

        return due_dates

def main():
    url = "https://www.utrgv.edu/financial-services-comptroller/departments/payroll-and-tax-compliance/payroll-schedules-and-deadlines/index.htm"
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    semi_monthly_table = get_semi_monthly_table(soup)
    monthly_table = get_monthly_table(soup)

    semi_monthly_due_dates = get_semi_monthly_due_dates(semi_monthly_table)
    monthly_due_dates = get_monthly_due_dates(monthly_table)

if __name__ == "__main__":
    main()
