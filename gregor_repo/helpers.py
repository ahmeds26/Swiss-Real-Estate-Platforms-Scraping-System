from selenium import webdriver
from selenium.webdriver import ChromeOptions
import undetected_chromedriver as uc
import csv
import os
import time
import json
import re
import glob
import json5
import codecs

def get_app_path():
    return os.getcwd()
    
def create_folder(folder_relative_path):
    directory_path = os.path.join(get_app_path(), folder_relative_path)
    if os.path.exists(directory_path): return
    os.mkdir(directory_path)

def create_csv_file(folder_relative_path, file_name, columns_headers):
    csv_file_path = os.path.join(os.getcwd(), folder_relative_path, f"{file_name}.csv")
    if os.path.exists(csv_file_path): return
    csv_file = open(csv_file_path, 'w', newline='', encoding='utf-8')
    csv_file_writer = csv.writer(csv_file, dialect='excel')
    csv_file_writer.writerow(columns_headers)
    csv_file.close()

def write_to_csv(folder_relative_path, file_name, data_array):
    csv_file_path = os.path.join(os.getcwd(), folder_relative_path, f"{file_name}.csv")
    
    csv_file = open(csv_file_path, 'a', newline='', encoding='utf-8')
    csv_file_writer = csv.writer(csv_file, dialect='excel', quoting=csv.QUOTE_ALL)
    if type(data_array[0]) is list:
        for i in data_array:
            csv_file_writer.writerow(i)
    else:
        csv_file_writer.writerow(data_array)
    csv_file.close()

def read_csv_file(folder_relative_path, file_name):
    csv_file_path = os.path.join(os.getcwd(), folder_relative_path, f"{file_name}.csv")

    with open(csv_file_path, encoding='utf-8') as csv_file:
        csv_file_rows = list(csv.reader(csv_file))[1:]
    for row in csv_file_rows:
        if not row: csv_file_rows.remove(row)
    return csv_file_rows

def create_json_file(folder_relative_path, file_name):
    json_file_path = os.path.join(os.getcwd(), folder_relative_path, f"{file_name}.json")
    if os.path.exists(json_file_path): return

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump([], json_file, indent=4, ensure_ascii=False)

def write_to_json(folder_relative_path, file_name, data_array):
    json_file_path = os.path.join(os.getcwd(), folder_relative_path, f"{file_name}.json")
    
    with open(json_file_path, 'r', encoding='utf-8-sig') as json_file:
        json_file_data = json.load(json_file)
        json_file_data.extend(data_array)
    with open(json_file_path, 'w', encoding='utf-8-sig') as json_file:
        json.dump(json_file_data, json_file, indent=4, ensure_ascii=False)

def dict_to_list(dictionary):
    return [list(list(dictionary.values())[v].values()) for v in range(0, len(list(dictionary.values())))]

def combine_two_lists_to_dict_to_list(list_1, list_2):
    if type(list_2[0]) != list:
        return [dict(zip(list_1, list_2))]
    else:
        return [dict(zip(list_1, list_2[f])) for f in range(0, len(list_2))]
    
      
def get_undetected_driver():

    options = ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    
    driver = uc.Chrome(options=options)

    return driver


def get_driver():

    options = ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})
    
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