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
from headers import icase_search_headers
from helpers import *
import time
import os



def icasa_search(driver, flag: int = 1):

    driver.get("https://icasa.ch/")
    time.sleep(5)
    try:
        cookie_alert = driver.find_element(By.ID, 'onetrust-reject-all-handler')
        cookie_alert.click()
        time.sleep(5)
    except:
        pass

    if flag == 1:
        buy_button = driver.find_element(By.LINK_TEXT, 'Buy')
        buy_button.click()
        time.sleep(10)
    else:
        rent_button = driver.find_element(By.LINK_TEXT, 'Rent')
        rent_button.click
        time.sleep(10)

    print("\n>>> Getting Search Page:: 1")
    current_page = driver.page_source
    current_soup = bs(current_page, 'html.parser')

    current_cards = current_soup.select('#propertyResults')[0].find_all('div', attrs={'class': 'propertycard'})
    print(len(current_cards))

    for p in range(2, 251):
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'archive-properties__pagination').find_elements(By.TAG_NAME, 'li')[-1]
            next_button.click()
            time.sleep(7)
        except:
            break
        print("\n>>> Getting Search Page:: ", str(p))
        next_page = driver.page_source
        next_soup = bs(next_page, 'html.parser')

        next_cards = next_soup.select('#propertyResults')[0].find_all('div', attrs={'class': 'propertycard'})
        print(len(next_cards))
        current_cards.extend(next_cards)

    total_cards = []
    for c in range(0, len(current_cards)):
        try:
            card_category = current_cards[c].find('a', attrs={'class': 'propertycard__category'}).text.strip() if len(current_cards[c].find('a', attrs={'class': 'propertycard__category'}).text.strip()) != 0 else "NA"
        except:
            card_category = ""
        try:
            card_url = "https://icasa.ch" + current_cards[c].find('a', attrs={'class': 'propertycard__category__link'}).get('href')
        except:
            card_url = ""
        try:
            card_image = current_cards[c].find('div', attrs={'class': 'propertycard__image'}).get('style').replace("background-image:url", "")[2:-2]
        except:
            card_image = ""
        try:
            card_price = current_cards[c].find('div', attrs={'class': 'propertycard__price'}).text.replace("'", ",").strip()
        except:
            card_price = ""
        try:
            card_price_value = int(current_cards[c].find('div', attrs={'class': 'propertycard__price'}).text.replace("CHF", "").replace(".-", "").replace("'", "").strip())
        except:
            card_price_value = 0
        try:
            card_address = current_cards[c].find('span', attrs={'itemprop': 'streetAddress'}).text.strip()
        except:
            card_address = ""
        try:
            card_locality = current_cards[c].find('span', attrs={'itemprop': 'addressLocality'}).text.strip()
        except:
            card_locality = ""
        try:
            card_region = current_cards[c].find('span', attrs={'itemprop': 'addressRegion'}).text.strip()
        except:
            card_region = ""
        try:
            card_postalcode = current_cards[c].find('span', attrs={'itemprop': 'postalCode'}).text.strip()
        except:
            card_postalcode = ""
        try:
            card_country = current_cards[c].find('span', attrs={'itemprop': 'addressCountry'}).text.strip()
        except:
            card_country = ""
        try:
            card_latitude = current_cards[c].find('meta', attrs={'itemprop': 'latitude'}).get('content')
        except:
            card_latitude = ""
        try:
            card_longitude = current_cards[c].find('meta', attrs={'itemprop': 'longitude'}).get('content')
        except:
            card_longitude = ""
        try:
            card_number_of_rooms = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Rooms":
                    card_number_of_rooms = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.strip()
                    break
        except:
            card_number_of_rooms = ""
        try:
            card_floor = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Floor":
                    card_floor = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.strip()
                    break
        except:
            card_floor = ""
        try:
            card_year_built = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Year built":
                    card_year_built = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.strip()
                    break
        except:
            card_year_built = ""
        try:
            card_use = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Use":
                    card_use = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.strip()
                    break
        except:
            card_use = ""
        try:
            card_plot_area = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Plot area":
                    card_plot_area = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.replace("\u2019", "").split(" ")[0]
                    break
        except:
            card_plot_area = ""
        try:
            card_living_space = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Living space":
                    card_living_space = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.replace("'", "").split(" ")[0]
                    break
        except:
            card_living_space = ""
        try:
            card_floor_space = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Floorspace":
                    card_floor_space = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.replace("'", "").split(" ")[0]
                    break
        except:
            card_floor_space = ""
        try:
            card_total_floor_area = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Total floor area":
                    card_total_floor_area = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.replace("'", "").split(" ")[0]
                    break
        except:
            card_total_floor_area = ""
        try:
            card_sia_gv_volume = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "SIA-GV":
                    card_sia_gv_volume = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.replace("\u2019", "").split(" ")[0]
                    break
        except:
            card_sia_gv_volume = ""
        try:
            card_rent_squared_meters_month = ""
            card_info_table_list = current_cards[c].find('table', attrs={'class': 'propertycard__infotable'}).find_all('tr')
            for r in range(0, len(card_info_table_list)):
                if card_info_table_list[r].select('.propertycard__infotable__left')[0].text.strip() == "Rent / m² / month":
                    card_rent_squared_meters_month = card_info_table_list[r].select('.propertycard__infotable__right')[0].text.strip()
                    break
        except:
            card_rent_squared_meters_month = ""

        card = [card_category, card_url, card_image, card_price, card_price_value, card_address, card_locality, card_region, card_postalcode, card_country, 
                card_latitude, card_longitude, card_number_of_rooms, card_floor, card_year_built, card_use, card_plot_area, card_living_space, card_floor_space, 
                card_total_floor_area, card_sia_gv_volume, card_rent_squared_meters_month]
        total_cards.append(card)

    print(len(total_cards))
    return total_cards
        

if __name__ == "__main__":

    type_id = 1   # 1 for buy, 2 for rent

    output_folder = "ICasa Data"
    output_search_folder = "Search Results"
    if type_id == 1:
        search_output_filename = "icasa_buy_search_results"
    else:
        search_output_filename = "icasa_rent_search_results"

    create_folder(os.path.join(output_folder))
    create_folder(os.path.join(output_folder, output_search_folder))

    create_csv_file(os.path.join(output_folder, output_search_folder), search_output_filename, icase_search_headers)

    driver = get_undetected_driver()

    search_results = icasa_search(driver, type_id)

    write_to_csv(os.path.join(output_folder, output_search_folder), search_output_filename, search_results)

    quit_driver(driver)