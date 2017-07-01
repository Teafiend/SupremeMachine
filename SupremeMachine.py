# Currently does not work; Supreme added captcha that
# seems impenetrable with Selenium... May have to switch
# to a different technology or discontinue bot development.
# Therefore, SupremeMachine (this program) will be placed on
# indefinite hold until I can find a way to circumvent the captcha issue.
# The following code will be left as a legacy example of how
# one can use Selenium to build a an efficient webstore bot.

# TODO: Store hashed credit and billing info in a database and associate them
# with usernames and passwords.
# TODO: Store all user information in a text file and parse
# at runtime or through a seperate config script.
# TODO: Migrate from using CSS selectors for form elements
# to a name-independant scraping method; probably HTML structure
# based rather than CSS based.

# Requires an installation of Chromium as well as chromedriver executable
# to be added to PATH environment variable. Alternatively, could add
# symbolic link to chromedriver in local bin directory.

import urllib.request
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

ROOT_URL = "http://www.supremenewyork.com"

DEV_MODE = True

REFRESH_RATE = 1 # refreshes per second
START_REFRESHING_AT = 57 # minutes after the hour
WAIT_ACCURACY = 60 # seconds

ORDER_BILLING_NAME = "foobar"
ORDER_EMAIL = "foobar"
ORDER_TL = "foobar"
BILLING_ADDRESS = "foobar"
ORDER_BILLING_ZIP = "foobar"
ORDER_BILLING_CITY = "foobar"
ORDER_BILLING_STATE = "foobar"
ORDER_BILLING_COUNTRY = "foobar"

CREDIT_CARD_TYPE = "foobar"
CREDIT_CARD_NUMBER = "foobar"
CREDIT_CARD_MONTH = "foobar"
CREDIT_CARD_YEAR = "foobar"
CCV = "foobar"


class SupremeMachine:
    def __init__(self, color, keywords, size, category):
        self.color = color
        self.keywords = keywords
        self.size = size
        self.url_extension = "/shop/all/" + category
        self.start_time = 0
        if DEV_MODE:
            self.driver = webdriver.Chrome() # Make sure chromedriver is in PATH, use this line for testing
        else:
            self.driver = webdriver.PhantomJS() # Also requires chromedriver to be in PATH, use this line for production

    # TODO: Iterate through list items instead of going item-by-item to avoid errors from CSS class name changes.
    def complete_form(self):
        self.complete_shipping_info()
        self.complete_credit_info()
        self.driver.find_element_by_css_selector("input#order_terms + ins").click()
        file = open('purchase_status.txt', 'r')
        if len(file.readline()) > 0:
            print("ALREADY PURCHASED")
            file.close()
            return
        self.driver.find_element_by_name("commit").click()
        file = open('purchase_status.txt', 'w')
        file.write('1')
        file.close()
        print("ITEM PURCHASED: {}".format(time.clock()-self.start_time))

    def complete_shipping_info(self):
        self.driver.find_element_by_id('order_billing_name').send_keys(ORDER_BILLING_NAME)
        self.driver.find_element_by_id('order_email').send_keys(ORDER_EMAIL)
        self.driver.find_element_by_id('order_tl').send_keys(ORDER_TL)
        self.driver.find_element_by_id('bo').send_keys(BILLING_ADDRESS)
        self.driver.find_element_by_id('order_billing_zip').send_keys(ORDER_BILLING_ZIP)
        self.driver.find_element_by_id('order_billing_city').send_keys(ORDER_BILLING_CITY)
        Select(self.driver.find_element_by_id('order_billing_state')).select_by_value(ORDER_BILLING_STATE)
        Select(self.driver.find_element_by_id('order_billing_country')).select_by_value(ORDER_BILLING_COUNTRY)

    def complete_credit_info(self):
        Select(self.driver.find_element_by_id('credit_card_type')).select_by_value(CREDIT_CARD_TYPE)
        self.driver.find_element_by_id('cnb').send_keys(CREDIT_CARD_NUMBER)
        Select(self.driver.find_element_by_id('credit_card_month')).select_by_value(CREDIT_CARD_MONTH)
        Select(self.driver.find_element_by_id('credit_card_year')).select_by_value(CREDIT_CARD_YEAR)
        self.driver.find_element_by_id('vval').send_keys(CCV)

    def purchase_item(self, item: 'HTML Element'):
        self.driver.get(ROOT_URL + item.div.a['href'])
        try:
            size_element = self.driver.find_element_by_id("size")
        except:
            print("SOLD OUT at {}.".format(datetime.datetime.now()))
            return
        
        if size_element.get_attribute("type") != "hidden":
            Select(size_element).select_by_visible_text(self.size)
            
        self.driver.find_element_by_name('commit').click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "cart")))
        self.driver.get(ROOT_URL + "/checkout")
        self.complete_form()

    def select_correct_item(self, items: list) -> None or 'HTML Element':
        for item in items:
            if self.color in item.div.p.a.string.lower():
                for keyword in self.keywords:
                    if keyword in item.div.h1.a.string.lower():
                        return item
        return None

    def poll_website(self):
        #wait_until(START_REFRESHING_AT, WAIT_ACCURACY)
        self.driver.get(ROOT_URL)
        print('Test started at {}.'.format(datetime.datetime.now()))
        while True:
            time.sleep(1 / REFRESH_RATE)
            items = self.get_page_items()
            selected_item = self.select_correct_item(items)
            if selected_item is not None:
                print('Correct item found at {}.'.format(datetime.datetime.now()))
                self.start_time = time.clock()
                self.purchase_item(selected_item)
                return

    def get_page_items(self):
        page = download_page_html(ROOT_URL + self.url_extension)
        soup = BeautifulSoup(page, 'html.parser')
        return soup.find_all('article')


def download_page_html(url: str) -> bytes:
    request = urllib.request.urlopen(url)
    return request.read()


def wait_until(minutes: int, accuracy: int):
    while not (datetime.datetime.now().minute >= START_REFRESHING_AT and datetime.datetime.now().hour == 7):
        time.sleep(accuracy)
        print("Sleeping: {}".format(datetime.datetime.now()))


def get_user_input():
    while True:
        color = input("Enter item color: ").lower()
        keywords = input("Enter keyword(s): ").lower().split()
        size = input("Enter item size: ").capitalize()
        category = input("Enter item category: ").lower()
        correct = input("Is the above information correct? ('yes' to continue, 'no' to restart): ").strip().lower()
        if correct == 'yes':
            return color, keywords, size, category


def execute_program():
    options = get_user_input()
    bot = SupremeMachine(*options)
    bot.poll_website()


if __name__ == "__main__":
    execute_program()
