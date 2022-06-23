import math
import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

stocks = ""

most_active_base_url = "https://au.finance.yahoo.com/cryptocurrencies?offset="
most_active_ext_url = "&count="
results_per_page = 25

number_of_results = 396  # The number of results that have been found on the page

# The calculated number of pages that can be checked that will always have 100 stocks (minus 1 because it is an offset)
number_of_pages_to_check = math.floor(number_of_results / results_per_page) - 1


# Function that returns the compiled url
def most_active_url(offset):
    return most_active_base_url + str(offset) + most_active_ext_url + str(results_per_page)


# Check all pages and save a csv of all the found stocks
for i in range(number_of_pages_to_check):

    print("Scraping Stock From Page: " + str(i))

    # Set up the Chrome Browser (New browser each time because it was running into unexpected loading error (Chrome Crash))
    options = Options()
    options.page_load_strategy = 'none'  # Setting Selenium to this makes it continue once main elements have been loaded
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Create the url link for the stock table then open it on the browser
    url = most_active_url(i * results_per_page)

    # Get the real webpage of the stock table
    driver.get(url)

    # Wait until the bare minimum has been loaded on the page
    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.ID, 'scr-res-table')))
    driver.execute_script("window.stop();")

    # Parse the Table to a list of stocks
    list_d = pd.read_html(driver.page_source)[0]
    df = pd.DataFrame(list_d)

    # Close the Chrome browser because info has been loaded
    driver.close()

    # Iterate through the dataframe and output the stocks
    for index, row in df.iterrows():
        stocks += str(row['Symbol']) + ","

    # Save the stock list to a csv
    with open('yahoo_finance_symbols/main_crypto_listx.csv', 'w') as f:
        f.write(stocks)
