import bot.constants_ir
import bot.constants_uk
import bot.scrape
import sys

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from chainbreaker_api import ChainBreakerScraper
import warnings
warnings.filterwarnings("ignore")

from utils.env import get_config
config = get_config()

from logger.logger import get_logger
logger = get_logger(__name__, level = "DEBUG", stream = True)

def enterAdultWork(constants, driver: Chrome):
    # Enter adult work.
    driver.get(constants.SITE)
    logger.info("Current URL: " +  str(driver.current_url))

    # Select country and accept.
    tds = driver.find_elements(By.TAG_NAME, "td")
    
    # Find Europe and click it.
    for td in tds:
        try:
            a = td.find_element(By.TAG_NAME, "a")
            if a.text == "Europe":
                a.click()
                break
        except:
            pass

    # Now, search for the countries of interest.
    for td in tds: 
        if td.get_attribute("id") == constants.COUNTRY_CODE:
            a = td.find_element(By.TAG_NAME, "a")
            a.click()
            break

    #driver.find_element_by_id(constants.COUNTRY_CODE).click()
    driver.switch_to.alert.accept()

    # Display all advertisements.
    for tab in driver.find_elements(By.CLASS_NAME, "HomePageTabLink"):
        if tab.get_attribute("title") == "All Escorts":
            tab.click()
            break

    # Filter by asian people.
    driver.find_element(By.XPATH, "//select[@name='question_7']/option[text()='Asian']").click()

    # Click search button.
    driver.find_element(By.NAME, "btnSearch").click()

def main(constants):
    endpoint = config["ENDPOINT"]
    user = config["USERNAME"]
    password = config["PASSWORD"]
    
    logger.warning("Parameters passed to scraper: " + endpoint + ", " + user + ", " + password)
    client = ChainBreakerScraper(endpoint)

    res = client.login(user, password)
    if type(res) != str:
        logger.critical("Login was not successful.")
        sys.exit()
    else: 
        logger.warning("Login was successful.")

    # Crear driver.
    logger.info("Open Chrome")
    if config["DEBUG"] == "TRUE":
        driver = webdriver.Chrome(executable_path="./chromedriver.exe")
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = config["GOOGLE_CHROME_BIN"]
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path= config["CHROMEDRIVER_PATH"], chrome_options=chrome_options)

    wait = WebDriverWait(driver, 10)
    enterAdultWork(constants, driver)

    count_announcement = 1

    # Page lists.
    for page in range(1, constants.MAX_PAGES + 1):
        logger.warning("# Page: " + str(page))

        # Get list of ads.
        ads = driver.find_elements(By.CLASS_NAME, "Padded")

        for ad in ads:

            userId = 0
            try:
                userId = ad.find_element(By.TAG_NAME, "a")
                userId = userId.get_attribute("href")
                userId = userId.replace("javascript:vU(", "")[:-1]
                url = "https://www.adultwork.com/ViewProfile.asp?UserID=" + userId
            except: 
                continue

            if client.get_status() != 200:
                logger.error("Endpoint is offline. Service stopped.", exc_info = True)
                driver.quit()
                sys.exit()

            info_ad = constants.SITE_NAME + ", #ad " + str(count_announcement) + ", page_link " + url
            id_ad = userId

            if client.does_ad_exist(id_ad, constants.SITE_NAME, constants.COUNTRY):
                logger.warning("Ad already in database. Link: " + url)
                continue
            else:
                logger.warning("New Ad. " + info_ad)
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
            logger.warning("Ad correctly loaded.")

         
            # Save values in dictionary.
            dicc = {}
            dicc["id_page"] = userId
            dicc["url"] = url

            # Scrap ad.
            ad_record = bot.scrape.scrap_ad_link(client, driver, dicc)
            count_announcement += 1

            # Return to pagination.
            #driver.get(current_url)
            driver.close()
            driver.switch_to.window(original_window)
         

        # Return the menu.
        # Change pagination with button.
        try:
            driver.find_element(By.XPATH, "//select[@name='cboPageNo']/option[text()='{number}']".format(number = page)).click()
        except:
            continue
    # Stop driver.
    driver.quit()

def execute_scraper():
    main(constants = bot.constants_uk)
    main(constants = bot.constants_ir)
