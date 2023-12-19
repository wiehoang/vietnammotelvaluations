###Motel Rental Valuations in Vietnam

##Crawl data
#Import libraries
import pandas as pd
import re
import time
import googlemaps
from seleniumbase import Driver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

#Setup a new undetected Chromedriver
driver = Driver(uc=True, headless=True)

#Function to crawl a single motel info
def single_motel_info(item):
    driver.find_elements(By.CLASS_NAME, 'pr-container')[item].click()
    time.sleep(3)
    
    #Get price info
    price = driver.find_elements(By.CLASS_NAME, 're__pr-short-info-item')[0].text.split('\n')[1]
    if ',' in price.split(' ')[0]:
        price_by_vnd = int(price.split(' ')[0].replace(',',''))*100000
    elif 'Th' in price.split(' ')[0]:
        price_by_vnd = ''
    else:
        price_by_vnd = int(price.split(' ')[0])*1000000

    #Get area info
    area = driver.find_elements(By.CLASS_NAME, 're__pr-short-info-item')[1].text.split('\n')[1]
    if ',' in area.split(' ')[0]:
        area_by_square_meter = round(float(area.replace(',', '.').split(' ')[0]))
    else:
        area_by_square_meter = int(area.split(' ')[0])

    #Get address info
    address_detail = driver.find_element(By.CLASS_NAME, 'js__pr-address').get_attribute('innerHTML').split(',')
    ##Get street name
    street_ext = address_detail[0:-3]
    street = ''.join(street_ext)
    ##Get ward name
    ward_ext = address_detail[-3].strip()
    if 'P.' in ward_ext or 'Ph' in ward_ext:
        new_ward_ext = ward_ext.split(' ')[1:]
        ward = ' '.join(new_ward_ext)
    else:
        ward = ward_ext
    ##Get district name
    dist_ext = address_detail[-2].strip()
    if 'Q.' in dist_ext or 'Qu' in dist_ext:
        new_dist_ext = dist_ext.split(' ')[1:]
        dist = ' '.join(new_dist_ext)
    else:
        dist = dist_ext
    ##Get city name
    city = address_detail[-1].strip()
    
    #Get motel link
    link = driver.current_url
    
    #Get map info
    gg_map = driver.find_element(By.CLASS_NAME, 're__pr-map').find_element(By.TAG_NAME, 'iframe').get_attribute('data-src')
    gg_map_ext = gg_map.split('q=')[1].split('&key')[0].split(',')
    latitude = gg_map_ext[0]
    longitude = gg_map_ext[1]
    
    #Wrap up all info
    motel_data = {'City':city, 'District':dist, 'Price_by_vnd':price_by_vnd, 'Area_by_square_meter':area_by_square_meter, 'Street_name': street, 'Ward': ward, 'Link': link, 'Latitude': latitude, 'Longitude': longitude}
    return motel_data

#Function to crawl motel info in full page
motel_data_by_number_of_page = []

def motel_info_by_number_of_page(page_url, page_start, page_end): #Choose 1 number for both page_start & page_end if you want to crawl only 1 page
    for i in range(page_start, page_end+1):
        new_page_url = f'{page_url}/p{i}'
        driver.get(new_page_url)
        time.sleep(10) #Increase number if you have a slow internet connection
        number_of_motel_in_page = driver.find_elements(By.CLASS_NAME, 'pr-container')
        for item in range(len(number_of_motel_in_page)):
            single_motel_data = single_motel_info(item)
            driver.back()
            motel_data_by_number_of_page.append(single_motel_data)
            driver.implicitly_wait(10) #Increase number if you have a slow internet connection
    return motel_data_by_number_of_page
    driver.quit()

#Convert into dataframe
df = pd.DataFrame(data = motel_data_by_number_of_page, columns = motel_data_by_number_of_page[0].keys())

#Double check data
number_of_row = int(input('Number of row you want to view: '))
df.info()

#Export data in csv
df.to_csv('motel_data_by_number_of_pages.csv', index=False, encoding='utf-8-sig') #Change a file name if you want


#Step 2: Fix and fulfil data
df = pd.read_csv(r'C:\Users\Wie\motel_data_by_number_of_pages.csv')
df1 = df.copy()

df1.eq('').sum() #Check if the columns contain empty string
df1.isna().sum() #Check if the columns contain NaN

#Check and drop NaN value in Price_by_vnd column
df1[df1['Price_by_vnd'].isna()]
df1.dropna(194, axis=0, inplace=True)

#Check and drop NaN value in Street_name column
df1[df1['Street_name'].isna()]
df1.dropna(axis=0, inplace=True)

#Check and drop duplicated row
df1.duplicated(subset=['Price_by_vnd','Street_name','Latitude','Longitude']).sum() #Check duplicated values
df1.drop_duplicates(subset=['Price_by_vnd','Street_name','Latitude','Longitude'], inplace=True) #Drop duplicate values

#Check unique values and fix if they are mistyped in each columns
df1['City'].unique()
df1['City'].replace(to_replace='Hồ Chí Minh.', value='Hồ Chí Minh', inplace=True)

#Export data in csv
df1.to_csv('motel_data_by_number_of_pages_cleaned.csv', index=False, encoding='utf-8-sig') #Change a file name if you want
