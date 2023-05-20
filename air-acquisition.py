#!/usr/bin/env python
# coding: utf-8

'''
For the data acquisition Selenium framework and Firefox are used
'''

#!pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
import json
import pandas as pd

### Download geckodriver to your local folder
driver = webdriver.Firefox(executable_path='./geckodriver')

driver.get('https://data.public.lu/fr/datasets/qualite-air-reseau-telemetrique/')
driver.find_elements(By.CSS_SELECTOR, ".fr-pagination__link.fr-pagination__link--last")[0].click()
rez = []

def extract_links(l):
    for i in l:
        rez.append(i.get_attribute('href'))

links = driver.find_elements(By.CSS_SELECTOR, ".fr-btn.fr-btn--sm.fr-icon-download-line")
extract_links(links)


while int(driver.find_elements(By.XPATH, "//*[@aria-current='page']")[2].text) != 1:
    driver.find_elements(By.CSS_SELECTOR, ".fr-pagination__link.fr-pagination__link--prev.fr-pagination__link--lg-label")[0].click()
    time.sleep(2)
    links = driver.find_elements(By.CSS_SELECTOR, ".fr-btn.fr-btn--sm.fr-icon-download-line")
    extract_links(links)

data = []
def extract_data_from_json(json_data):
    station_columns = ['adr_num_street', 'date', 'code', 'hour', 'adr_street', 'adr_city', 'luref_y', 'luref_x']
    for i in range(len(json_data)):
        station = json_data[i]["station"]
        for s in range(len(station)):
            o = station[s]
            if set(station_columns).issubset(set(pd.json_normalize(o).columns.to_list())):
                station_data = pd.json_normalize(o).iloc[0][station_columns]
                measurements = pd.json_normalize(o['data'])
                for m in range(len(measurements)):
                    #data.append()
                    data.append(pd.concat([station_data, measurements.iloc[m]]))


for i in range(len(rez)):
    response = requests.get(rez[i])
    
    if response.status_code == 200:
        json_data = response.json()
        extract_data_from_json(json_data)
    else:
        print("Failed to retrieve JSON data. Status code:", response.status_code)


data = pd.DataFrame(data, columns=['adr_num_street', 'date', 'code', 'hour', 'adr_street', 'adr_city',
       'luref_y', 'luref_x', 'indexRaw', 'polLabel', 'index', 'value']).reset_index()
data = data.drop('level_0', axis=1)
data.to_csv('air.denormalized.csv', index=False)

