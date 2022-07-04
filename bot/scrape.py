import bot.constants
import datetime
from dateutil.parser import parse
from chainbreaker_api import ChainBreakerScraper
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome

from logger.logger import get_logger
logger = get_logger(__name__, level = "DEBUG", stream = True)


keywords = ["Town", "County", "Region", "Country", "Nationality", "Member Since", "Age"]
map_keywords = {"Town": "city", "County": "place", "Region": "region", "Nationality": "nationality", "Member Since": "post_date", "Age": "age"}

def clean_string(string, no_space = False):   
    """
    Clean String.
    """
    if no_space:
        string = string.replace("  ","")
    string = string.strip()
    string = string.lower()
    string = string.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
    string = string.replace("\n"," ")
    return string

def get_dicc_fields(driver: Chrome) -> str:
    dicc = {}
    elements = driver.find_elements(By.TAG_NAME, "tr")
    for e in elements:
        tds = e.find_elements(By.TAG_NAME, "td")
        try:
            label, text = tds[0], tds[1]
            if label.get_attribute("class") != "Label":
                continue
            key = label.text.replace(":", "")
            if key in keywords:
                value = text.text.lower()
                new_key = map_keywords[key]
                dicc[new_key] = value
        except:
            continue
    return dicc

def assign_value(dicc: dict, key: str):
    if key in dicc:
        return dicc[key]
    return ""    

def getTitle(driver: Chrome):
    text = driver.find_element(By.CLASS_NAME, "PageHeading").text
    text = clean_string(text)
    return text

def getText(driver: Chrome):
    try:
        text = driver.find_element(By.ID, "content1").text
        text = clean_string(text)
        return text
    except:
        pass

    try:
        tds = driver.find_elements(By.TAG_NAME, value="td")
        text = ""
        for td in tds: 
            a = td.get_attribute("class") == "unSelectable"
            b = td.get_attribute("onselectstart") == "return false"
            c = td.get_attribute("unselectable") == "on"
            if (a and b and c):
                text += td.text + " "
            if td.text == "Frequently Asked Questions...":
                break
        return clean_string(text)
    except:
        return None
        
def getDateScrap():
    return datetime.date.today()

def getCellphone(driver: Chrome):
    bs = driver.find_elements(By.TAG_NAME, "b")
    for b in bs: 
        if b.get_attribute("itemprop") == "telephone":
            return b.text
    return None

def getPostDate(text: str):
    time = datetime.datetime.strptime(text, '%d/%m/%Y')  # año mes dia
    time = time.strftime("%Y-%m-%d")
    return time

def getAge(text: str):
    if text != "not specified":
        return ""
    else: return text

def scrap_ad_link(client: ChainBreakerScraper, driver, dicc: dict):
    
    # Get phone or whatsapp
    phone = getCellphone(driver)
    email = "" # Not provided in this website.
    if phone == None:
        logger.warning("Phone not found! Skipping this ad.")
        return None

    # Get fields.    
    dicc_fields = get_dicc_fields(driver)

    author = bot.constants.AUTHOR
    language = bot.constants.LANGUAGE
    link = dicc["url"]
    id_page = dicc["id_page"]
    title = getTitle(driver)
    text = getText(driver)
    if text == None:
        return None

    category = bot.constants.CATEGORY
    first_post_date = getPostDate(assign_value(dicc_fields, "post_date"))

    date_scrap = getDateScrap()
    website = bot.constants.SITE_NAME

    verified_ad = ""          # Not provided
    prepayment = ""           # Not provided
    promoted_ad = ""          # Not provided
    external_website = ""     # Not provided
    reviews_website = ""      # Not provided
    country = bot.constants.COUNTRY
    region = assign_value(dicc_fields, "region")
    city = assign_value(dicc_fields, "city")
    place = assign_value(dicc_fields, "place")

    latitude = ""  # Not provided.
    longitude = "" # Not provided.
    comments = []  # Doesnt have comments, just Q&A

    ethnicity = bot.constants.ETHNICITY
    nationality = assign_value(dicc_fields, "nationality")
    age = getAge(assign_value(dicc_fields, "age"))

    # Upload ad in database.
    data, res = client.insert_ad(author, language, link, id_page, title, text, category, first_post_date, date_scrap, website, phone, country, region, city, place, email, verified_ad, prepayment, promoted_ad, external_website,
            reviews_website, comments, latitude, longitude, ethnicity, nationality, age) # Eliminar luego
    # Log results.
    logger.info("Data sent to server: ")
    logger.info(data)
    logger.info(res.status_code)
    #print(res.text)
    if res.status_code != 200: 
        logger.error("Algo salió mal...")
    else: 
        logger.info("Éxito!")