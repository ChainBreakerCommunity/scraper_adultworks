# Adult works scraper.

import utils
import constants
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from chainbreaker_api import ChainBreakerScraper
import json
import os
import warnings
warnings.filterwarnings("ignore")

# Configure loggin file.
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')

def enterAdultWork(driver: webdriver):
    # Enter adult work.
    driver.get(constants.SITE)
    print("Current URL: ", driver.current_url)

    # Select UK and accept.
    driver.find_element_by_id("s_158").click()
    driver.switch_to.alert.accept()

    # Display all advertisements.
    for tab in driver.find_elements_by_class_name("HomePageTabLink"):
        if tab.get_attribute("title") == "All Escorts":
            tab.click()
            break

    # Filter by asian people.
    driver.find_element_by_xpath("//select[@name='question_7']/option[text()='Asian']").click()

    # Click search button.
    driver.find_element_by_name("btnSearch").click()

def main():
    with open("./config.json") as json_file: 
        data = json.load(json_file)

    endpoint = data["endpoint"]
    user = data["username"]
    password = data["password"]
    
    logging.warning("Parameters passed to scraper: " + endpoint + ", " + user + ", " + password)
    client = ChainBreakerScraper(endpoint)
    print("Trying to login now")
    sys.stdout.flush()

    res = client.login(user, password)
    if type(res) != str:
        logging.critical("Login was not successful.")
        print("Login was no successful")
        sys.stdout.flush()
        sys.exit()
    else: 
        logging.warning("Login was successful.")
        print("Login was successful.")
        sys.stdout.flush()

    # Crear driver.
    print("Open Chrome")
    sys.stdout.flush()
    driver = webdriver.Chrome(executable_path="../test/chromedriver.exe")
    
    #chrome_options = webdriver.ChromeOptions()
    #chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--no-sandbox")
    #driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    wait = WebDriverWait(driver, 10)
    enterAdultWork(driver)

    count_announcement = 1

    # Page lists.
    for page in range(1, constants.MAX_PAGES + 1):
        logging.warning("# Page: " + str(page))
        print("# Page: " + str(page))
        sys.stdout.flush()

        # Get list of ads.
        ads = driver.find_elements_by_class_name("Padded")

        for ad in ads:

            userId = 0
            try:
                userId = ad.find_element_by_tag_name("a")
                userId = userId.get_attribute("href")
                userId = userId.replace("javascript:vU(", "")[:-1]
                url = "https://www.adultwork.com/ViewProfile.asp?UserID=" + userId
            except: 
                continue

            if client.get_status() != 200:
                logging.error("Endpoint is offline. Service stopped.", exc_info = True)
                print("Endpoint is offline. Service stopped.")
                sys.stdout.flush()
                driver.quit()
                sys.exit()

            info_ad = constants.SITE_NAME + ", #ad " + str(count_announcement) + ", page_link " + url
            id_ad = userId

            if client.does_ad_exist(id_ad, constants.SITE_NAME, constants.COUNTRY):
                logging.warning("Ad already in database. Link: " + url)
                print("Ad already in database. Link: " + url)
                sys.stdout.flush()
                continue
            else:
                logging.warning("New Ad. " + info_ad)
                print("New Ad. " + info_ad)
                sys.stdout.flush()

            # Enter to the ad.
            original_window = driver.current_window_handle
            assert len(driver.window_handles) == 1

            # Click the link which opens in a new window
            driver.execute_script("window.open('');")

            # Wait for the new window or tab
            wait.until(EC.number_of_windows_to_be(2))

            # Loop through until we find a new window handle
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break

            # Load ad in the new window.
            driver.get(url)

            logging.warning("Ad correctly loaded.")
            print("Ad correctly loaded.")
            sys.stdout.flush()
         
            # Save values in dictionary.
            dicc = {}
            dicc["id_page"] = userId
            dicc["url"] = url

            # Scrap ad.
            ad_record = utils.scrap_ad_link(client, driver, dicc)
            count_announcement += 1

            # Return to pagination.
            #driver.get(current_url)
            driver.close()
            driver.switch_to.window(original_window)
         

        # Return the menu.
        # Change pagination with button.
        try:
            driver.find_element_by_xpath("//select[@name='cboPageNo']/option[text()='{number}']".format(number = page)).click()
        except:
            continue

if __name__ == "__main__":
    main()
