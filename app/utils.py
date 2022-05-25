import constants
import datetime
from dateutil.parser import parse
from chainbreaker_api import ChainBreakerScraper
import logging
from typing import List 
import sys
import selenium
from selenium import webdriver

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

def get_dicc_fields(driver: webdriver) -> str:
    dicc = {}
    elements = driver.find_elements_by_tag_name("tr")
    for e in elements:
        tds = e.find_elements_by_tag_name("td")
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

def getTitle(driver: webdriver):
    text = driver.find_element_by_class_name("PageHeading").text
    text = clean_string(text)
    return text

def getText(driver: webdriver):
    text = driver.find_element_by_id("content1").text
    text = clean_string(text)
    return text

def getDateScrap():
    return datetime.date.today()

def getCellphone(driver: webdriver):
    bs = driver.find_elements_by_tag_name("b")
    for b in bs: 
        if b.get_attribute("itemprop") == "telephone":
            return b.text
    return None

def getPostDate(text: str):
    time = datetime.datetime.strptime(text, '%d/%m/%Y')  # año mes dia
    time = time.strftime("%Y-%m-%d")
    return time

def scrap_ad_link(client: ChainBreakerScraper, driver, dicc: dict):
    
    # Get phone or whatsapp
    phone = getCellphone(driver)
    email = "" # Not provided in this website.
    if phone == None:
        logging.warning("Phone not found! Skipping this ad.")
        print("Phone not found! Skipping this ad.")
        sys.stdout.flush()
        return None

    # Get fields.    
    dicc_fields = get_dicc_fields(driver)

    author = constants.AUTHOR
    language = constants.LANGUAGE
    link = dicc["url"]
    id_page = dicc["id_page"]
    title = getTitle(driver)
    text = getText(driver)
    category = constants.CATEGORY
    first_post_date = getPostDate(assign_value(dicc_fields, "post_date"))

    date_scrap = getDateScrap()
    website = constants.SITE_NAME

    verified_ad = ""          # Not provided
    prepayment = ""           # Not provided
    promoted_ad = ""          # Not provided
    external_website = ""     # Not provided
    reviews_website = ""      # Not provided
    country = constants.COUNTRY
    region = assign_value(dicc_fields, "region")
    city = assign_value(dicc_fields, "city")
    place = assign_value(dicc_fields, "place")

    latitude = ""  # Not provided.
    longitude = "" # Not provided.
    comments = []  # Doesnt have comments, just Q&A

    ethnicity = ""
    nationality = assign_value(dicc_fields, "nationality")
    age = assign_value(dicc_fields, "age")

    # Upload ad in database.
    status_code = client.insert_ad(author, language, link, id_page, title, text, category, first_post_date, date_scrap, website, phone, country, region, city, place, email, verified_ad, prepayment, promoted_ad, external_website,
            reviews_website, comments, latitude, longitude, ethnicity, nationality, age) # Eliminar luego
    print(status_code)
    if status_code != 200: 
        print("Algo salió mal...")
    else: 
        print("Éxito!")