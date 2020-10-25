#!/usr/bin/env python

import requests
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

def main():
    url = "https://www.utrgv.edu/financial-services-comptroller/departments/payroll-and-tax-compliance/payroll-schedules-and-deadlines/index.htm"
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    semi_monthly_table = get_semi_monthly_table(soup)
    monthly_table = get_monthly_table(soup)

if __name__ == "__main__":
    main()
