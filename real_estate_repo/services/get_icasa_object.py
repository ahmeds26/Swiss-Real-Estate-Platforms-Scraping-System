from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup as bs
import undetected_chromedriver as uc
from headers import contacts_headers, contacts_used_ids_headers, objects_headers
from api_check import check_contact_with_api, check_object_with_api
from helpers import *
from itertools import count
import phonenumbers
import time
import os


def get_app_path():
    return os.getcwd()

def get_driver():

    options = ChromeOptions()
    #options.add_experimental_option("prefs", {
    #    "profile.default_content_setting_values.media_stream_mic": 1,
    #    "profile.default_content_setting_values.media_stream_camera": 1,
    #    "profile.default_content_setting_values.geolocation": 1,
    #    "profile.default_content_setting_values.notifications": 1,
    #    'intl.accept_laa    qz212nguages': 'en,en_US'
    #})
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    
    #driver = uc.Chrome(options=options)
    
    driver = webdriver.Chrome(options=options)
    return driver

def quit_driver(driver):
    try:
        driver.quit()
    except:
        pass

def get_object_category_id(rs_categories, object_category):

    if object_category.lower() in rs_categories.keys():
        object_category_id = rs_categories[object_category.lower()]
    elif " " in object_category:
        object_category_main = object_category.split()[-1]
        object_category_id = rs_categories["other"]
        for k in rs_categories.keys():
            if object_category_main.lower() in k:
                object_category_id = rs_categories[k]
    else:
        object_category_id = rs_categories["other"]

    return object_category_id

def check_contact_in_used_ids(used_ids, contact_first, contact_last):
    for i in range(0, len(used_ids)):
        if used_ids[i][1].strip() == contact_first.strip() and used_ids[i][2].strip() == contact_last.strip():
            contact_id = used_ids[i][0]
            return contact_id
    return False

def format_phone_number(phone_number, country_code):
    num = phonenumbers.parse(phone_number, country_code)
    formatted_num = phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    return formatted_num

def get_icasa_object(driver, input_row, portal_id, vendor_id, type_id, advertiser_id, rs_categories):

    
    object_latitude = input_row[10]
    object_longitude = input_row[11]
    object_advertiser_id = advertiser_id
    object_category_id = ""
    
    
    object_url = input_row[1]
    driver.get(object_url)
    time.sleep(10)

    object_page = driver.page_source
    object_soup = bs(object_page, 'html.parser')

    try:
        object_no_longer_exists = object_soup.select("h1.page__title")[0].text.strip()
        if object_no_longer_exists == "Error 404":
            return ([], [])
    except:
        pass

    try:
        object_title_part1 = object_soup.select("div.single__content__primary")[0].find("h1").text.strip().split("\n")[0].strip()
        object_title_part2 = object_soup.select("div.single__content__primary")[0].find("h1").text.strip().split("\n")[1].strip()
        object_title = object_title_part1 + ". " + object_title_part2
    except:
        object_title = ""
    try:
        #object_description = object_soup.select("div#singleDescription")[0].find("h3").next_sibling.get_text(separator=". ").replace("\x96", "-").strip()
        object_description = object_soup.select("div#singleDescription")[0].find("span", attrs={"itemprop": "description"}).text.strip()
    except:
        object_description = ""
    try:
        object_full_address = ""
        object_street_address = ""
        object_zip_code = ""
        object_city = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[0].find('table').tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Address":
                object_full_address_element = object_key_facts_list[f].td
                object_full_address = object_key_facts_list[f].td.text.strip()
                for b in object_full_address_element.find_all('br'):
                    b.replace_with('\n')
                if any(char.isdigit() for char in object_full_address_element.text.split("\n")[0].strip()):
                    object_house_number = object_full_address_element.text.split("\n")[0].split(" ")[-1].strip()
                    object_street_address = object_full_address_element.text.split("\n")[0].replace(object_house_number, "").strip()
                else:
                    object_house_number = ""
                    object_street_address = object_full_address_element.text.split("\n")[0].strip()
                object_zip_code = object_full_address_element.text.split("\n")[-1].strip().split(" ")[0].strip()
                object_city = object_full_address_element.text.split("\n")[-1].replace(object_zip_code, "").strip()                      
    except:
        object_full_address = ""
        object_street_address = ""
        object_zip_code = ""
        object_city = ""
    try:
        object_reference_number = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[0].find('table').tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Reference no.":
                object_reference_number = object_key_facts_list[f].td.text.strip()
    except:
        object_reference_number = ""
    try:
        object_category = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[0].find('table').tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Categories":
                object_category = object_key_facts_list[f].td.text.strip()
        object_category_id = get_object_category_id(rs_categories, object_category)
    except:
        object_category_id = ""
    try:
        object_available_from = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[0].find('table').tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Available from":
                object_available_from = object_key_facts_list[f].td.text.strip()
    except:
        object_available_from = ""
    try:
        object_floor_number = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[0].find('table').tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Floor":
                object_floor_number = object_key_facts_list[f].td.text.strip()
    except:
        object_floor_number = ""
    try:
        object_number_of_rooms = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[0].find('table').tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Rooms":
                object_number_of_rooms = object_key_facts_list[f].td.text.strip()
    except:
        object_number_of_rooms = ""

    try:
        object_price = ""
        object_price_value = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[1].select('table')[0].tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Sales price":
                object_price = object_key_facts_list[f].td.text.replace("\xa0", " ").strip()
                object_price_value = int(object_key_facts_list[f].td.text.strip().replace("\xa0", " ").replace("CHF", "").replace(".–", "").replace("’", "").strip())
    except:
        object_price = ""
        object_price_value = ""
    try:
        object_net_living_area = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[1].select('table')[1].tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Net living area":
                object_net_living_area = object_key_facts_list[f].td.text.split(" ")[0].replace("’", "").strip()
    except:
        object_net_living_area = ""
    try:
        object_land_area = ""
        object_key_facts_list = object_soup.select("div.single__content__primary")[0].find("div", attrs={'class': 'single__datatable'}).select('div.single__datatable__col')[1].select('table')[1].tbody.select('tr')
        for f in range(0, len(object_key_facts_list)):
            if object_key_facts_list[f].th.text.strip() == "Land area":
                object_land_area = object_key_facts_list[f].td.text.split(" ")[0].replace("’", "").strip()
    except:
        object_land_area = ""
    try:
        object_icasa_id = object_soup.select("div.single__visitbox")[0].select("div.single__boxblock")[0].text.strip().split("\n")[0].replace("iCasa-ID:", "").strip()
    except:
        object_icasa_id = ""
    try:
        object_images = []
        object_images_list = object_soup.select("ul#single__gallery")[0].find_all("div", attrs={"class": "item single__gallery__image"})
        for i in range(0, len(object_images_list)):
            image_url = "https://casagateway.ch" + object_images_list[i].get("style").replace("background-image: url('", "")[:-8]
            image_dict = {i+1: image_url}
            object_images.append(image_dict)
    except:
        object_images = []

    ## contact data
    object_contact_email = ""
    object_contact_id = ""
    try:
        object_contact_fullname = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[1].strong.text.strip()
        object_contact_firstname = object_contact_fullname.split(" ")[0].strip()
        object_contact_lastname = object_contact_fullname.split(" ")[-1].strip()
    except:
        object_contact_fullname = ""
        object_contact_firstname = ""
        object_contact_lastname = ""
    try:
        #object_contact_phone_number = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[1].select("div#mobileNumber")[0].select("span.behind-sticker")[0].text.strip()
        object_contact_phone_number = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[1].select("div.single__providerbox__company-phone")[0].select("span.behind-sticker")[0].text.strip()
        if object_contact_phone_number != "":
            object_contact_phone_number_normalized = format_phone_number(object_contact_phone_number, "CH")
        else:
            object_contact_phone_number_normalized = object_contact_phone_number.replace(" ", "")
    except:
        object_contact_phone_number = ""
        object_contact_phone_number_normalized = ""
    try:
        object_organization_title = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[2].select("div.company")[0].text.strip()
    except:
        object_organization_title = ""
    try:
        object_organization_house_number = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[2].select("div.company")[0].next_sibling.text.split(" ")[-1].strip()
    except:
        object_organization_house_number = ""
    try:
        object_organization_street_address = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[2].select("div.company")[0].next_sibling.text.replace(object_organization_house_number, "").strip()
    except:
        object_organization_street_address = ""
    try:
        object_organization_zip_code = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[2].select("div.company")[0].next_sibling.next_sibling.next_sibling.next_sibling.text.split(" ")[0].strip()
    except:
        object_organization_zip_code = ""
    try:
        object_organization_city = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[2].select("div.company")[0].next_sibling.next_sibling.next_sibling.next_sibling.text.split(" ")[-1].strip()
    except:
        object_organization_city = ""
    try:
        object_organization_country = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[2].select("div.company")[0].next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.text.strip()
    except:
        object_organization_country = ""
    try:
        object_organization_phone_number1 = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[2].select("div#phoneNumberCompany")[0].select("span.behind-sticker")[0].text.strip()
    except:
        object_organization_phone_number1 = ""
    try:
        object_organization_phone_number2 = object_soup.select("div.single__providerbox")[0].select("div.single__boxblock")[2].select("div#phoneNumberCompany")[1].select("span.behind-sticker")[0].text.strip()
    except:
        object_organization_phone_number2 = ""

    contact_row = [object_contact_id, object_contact_firstname, object_contact_lastname, object_organization_title, object_contact_email, object_contact_phone_number, 
                   object_organization_street_address, object_organization_house_number, object_organization_zip_code, object_organization_city, 
                   object_contact_phone_number_normalized, portal_id, vendor_id]
    
    object_row = [object_contact_id, portal_id, vendor_id, type_id, object_url, object_title, object_description, object_street_address, object_house_number, 
                  object_zip_code, object_city, object_latitude, object_longitude, object_price, object_net_living_area, object_land_area, object_category_id, 
                  object_price_value, object_advertiser_id]
    
    return (contact_row, object_row)


if __name__ == "__main__":

    portal_id = 12
    vendor_id = 8
    type_id = 1
    advertiser_id = ""

    output_folder = "ICasa Data"
    output_data_folder = "Objekte Kontakte Data"
    contacts_output_filename = "Kontakte"
    objects_output_filename = "Objekte"
    contacts_used_ids_filename = "contacts-used-ids"

    create_folder(os.path.join(output_folder, output_data_folder))
    create_csv_file(os.path.join(output_folder, output_data_folder), contacts_output_filename, contacts_headers)
    create_csv_file(os.path.join(output_folder, output_data_folder), objects_output_filename, objects_headers)
    create_csv_file(os.path.join(output_folder), contacts_used_ids_filename, contacts_used_ids_headers)

    #contacts_used_ids = read_csv_file(os.path.join(output_folder), contacts_used_ids_filename)

    #id_generator = count(start=len(contacts_used_ids)+1)

    input_folder = "Search Results"
    input_filename = "icasa-buy-search-results"

    input_categories = read_csv_file(os.path.join(output_folder), "rs_categories")
    categories = {}
    for c in range(0, len(input_categories)):
        category_name = "".join(input_categories[c][1].lower().replace("_", " ").split()).lower()
        category_id = input_categories[c][0]
        categories[category_name] = category_id

    input_rows = read_csv_file(os.path.join(output_folder, input_folder), input_filename)
    print(len(input_rows))

    driver = get_driver()

    #for r in range(0, len(input_rows)):
    for r in range(1000, 2000):

        current_object = input_rows[r]

        print("Row Number: ", str(r), " --> ", "Getting Object Data: ", current_object[1])
        print("\n\t\t Checking Object with api....")
        object_check_result = check_object_with_api(current_object[1])
        if object_check_result == False:
            print("\n\t\t\t Object not in the api database.... Scraping Object....")
            object_data = get_icasa_object(driver, input_rows[r], portal_id, vendor_id, type_id, advertiser_id, categories)
            if object_data == ([], []):
                print("\n\t\t\t\t Object no longer exists on ICasa ....")
                continue
            if int(object_data[1][9]) <= 2500:
                print("\n\t\t\t\t Object Zipcode less than 2500 ....")
                continue
            if object_data[0][5] == "":
                print("\n\t\t\t\t Contact has no phone number ....")
                continue
            print("\n\t\t\t\t Checking Contact with api....")
            contact_payload = {
                "first_name": object_data[0][1], 
                "last_name": object_data[0][2], 
                "organization_name": object_data[0][3]
            }
            contact_check_result = check_contact_with_api(contact_payload)
            if contact_check_result == "false":
                print("\n\t\t\t\t\t Contact not in the api database.... Saving Contact....")
                contacts_used_ids = read_csv_file(os.path.join(output_folder), contacts_used_ids_filename)
                id_generator = count(start=len(contacts_used_ids)+1)
                object_contact_id = check_contact_in_used_ids(contacts_used_ids, object_data[0][1], object_data[0][2])
                if object_contact_id:
                    #object_data[0][0] = object_contact_id
                    object_data[1][0] = object_contact_id
                    write_to_csv(os.path.join(output_folder, output_data_folder), objects_output_filename, object_data[1])
                    time.sleep(3)
                else:
                    object_contact_id = next(id_generator)
                    object_data[0][0] = object_contact_id
                    object_data[1][0] = object_contact_id
                    contact_used_id_row = [object_contact_id, object_data[0][1], object_data[0][2]]
                    write_to_csv(os.path.join(output_folder, output_data_folder), contacts_output_filename, object_data[0])
                    write_to_csv(os.path.join(output_folder, output_data_folder), objects_output_filename, object_data[1])
                    write_to_csv(os.path.join(output_folder), contacts_used_ids_filename, contact_used_id_row)
                    time.sleep(3)
            elif contact_check_result == "blocked":
                print("\n\t\t\t\t\t Contact is blocked.... Discarding Contact....")
            else:
                print("\n\t\t\t\t\t Contact is found.... Saving Contact....")
                object_data[1][-1] = contact_check_result
                contacts_used_ids = read_csv_file(os.path.join(output_folder), contacts_used_ids_filename)
                id_generator = count(start=len(contacts_used_ids)+1)
                object_contact_id = check_contact_in_used_ids(contacts_used_ids, object_data[0][1], object_data[0][2])
                if object_contact_id:
                    object_data[1][0] = object_contact_id
                    write_to_csv(os.path.join(output_folder, output_data_folder), objects_output_filename, object_data[1])
                    time.sleep(3)
                else:
                    object_contact_id = next(id_generator)
                    object_data[0][0] = object_contact_id
                    object_data[1][0] = object_contact_id
                    contact_used_id_row = [object_contact_id, object_data[0][1], object_data[0][2]]
                    write_to_csv(os.path.join(output_folder, output_data_folder), contacts_output_filename, object_data[0])
                    write_to_csv(os.path.join(output_folder, output_data_folder), objects_output_filename, object_data[1])
                    write_to_csv(os.path.join(output_folder), contacts_used_ids_filename, contact_used_id_row)
                    time.sleep(3)
                #object_contact_id = contact_check_result
                #contact_used_id_row = [object_contact_id, object_data[0][1], object_data[0][2]]
                #write_to_csv(os.path.join(output_folder, output_data_folder), contacts_output_filename, object_data[0])
                #write_to_csv(os.path.join(output_folder, output_data_folder), objects_output_filename, object_data[1])
                #write_to_csv(os.path.join(output_folder), contacts_used_ids_filename, contact_used_id_row)
                #time.sleep(3)
        else:
            print("\n\t\t\t Object is already in the api database.... Skipping Object....")

    quit_driver(driver)
    
    

    

