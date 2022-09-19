from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import ssl
from email.message import EmailMessage
import datetime

import smtplib
import pandas as pd
import requests
from bs4 import BeautifulSoup
from price_parser import Price
import schedule
import time


# config
SAVE_TO_CSV = True
SEND_MAIL = True
waitlist_CSV = "waitlist.csv"
aftertracking_CSV = "aftertracking.csv"

# Edit your email address
mail_user = ‘’
mail_pass = ‘’
mail_to = ‘’


def get_urls(csv_file):
    # Use pandas to read csv data
    dataframe = pd.read_csv(csv_file)
    return dataframe


def process_products(dataframe):
    updated_products = []
    # converting the DataFrame into a list of dictionaries.
    for product in dataframe.to_dict("records"):
        # automating web broser by using selenium...click functions to be added..
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(product["url"])
        page = driver.page_source
        product["price"] = get_price(page)
        product["result"] = product["price"] < product["expected_price"]
        updated_products.append(product)
    return pd.DataFrame(updated_products)


def get_response(url):
    response = requests.get(url)
    return response.text


def get_price(page_html):
    soup = BeautifulSoup(page_html, "lxml")
    try:
        el = soup.select_one(".item-price__normal")
        price = Price.fromstring(el.text)
    except:
        el = soup.select_one(".item-price__price-amount")
        price = Price.fromstring(el.text)

    return price.amount_float


def send_mail(dataframe):
    subject = 'Msg from you Indigo Tracker!'

    if dataframe[dataframe["result"]].to_string() == 'true':
        body = f"Good News! The price is lower than your expected price! BUY IT NOW! \n{datetime.datetime(2021, 9, 1)}\nThank you for trying INDIGO tracker~\nBest regards,\nXinyi"

    else:
        body = f"OOPS! It seems too expensive \n{datetime.datetime(2021, 9, 1)}\nThank you for trying INDIGO tracker~\nBest regards,\nXinyi"

    em = EmailMessage()
    em['Form'] = mail_user
    em["To"] = mail_to
    em['subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(mail_user, mail_to, em.as_string())


def main():
    dataframe = get_urls(waitlist_CSV)
    dataframe_updated = process_products(dataframe)
    if SAVE_TO_CSV:
        dataframe_updated.to_csv(aftertracking_CSV, index=False, mode="a")
    if SEND_MAIL:
        send_mail(dataframe_updated)


main()
# schedule.every().day.at("10:30").do(main)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
