#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import glob
import time
import re


# In[ ]:


url = 'https://www.nycenet.edu/offices/finance_schools/budget/DSBPO/allocationmemo/fy21_22/am_fy22_erf1.htm'

chrome_options = webdriver.ChromeOptions()
#save any files in the current working directory
#prefs = {'download.default_directory' : os.getcwd()}
#chrome_options.add_argument("--headless")
#chrome_options.add_experimental_option('prefs', prefs)
service = ChromeService(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(service = service, options=chrome_options)

driver.get(url)



# In[134]:


url = 'https://www.nycenet.edu/offices/finance_schools/budget/DSBPO/allocationmemo/fy21_22/am_fy22_pg1.htm'
url_prefix = 'https://www.nycenet.edu/offices/finance_schools/budget/DSBPO/allocationmemo/fy21_22/'
urls = []
categories = []
#convert the webpage to soup
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
#find the webpage body with event details
table = soup.find('table')

ran = False

for row in table:
    try:
        for a in row.find_all('a', href=True):
            if a.text == 'Arts Supplemental Funding through Fair Student Funding':
                ran = True
            if ran:
                urls.append(url_prefix + a['href'])
                categories.append(a.text)
    except:
        continue



# In[135]:


urls


# In[136]:


for i, category_title in enumerate(categories):
    categories[i] = re.sub("\\r|\\t|\\n","",category_title)
    
categories


# In[137]:


chrome_options = webdriver.ChromeOptions()
#save any files in the current working directory
#prefs = {'download.default_directory' : os.getcwd()}
#chrome_options.add_argument("--headless")
#chrome_options.add_experimental_option('prefs', prefs)
service = ChromeService(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(service = service, options=chrome_options)

driver.get(url)


# In[138]:


categories_dict = {}

for i, url in enumerate(urls):
    driver.get(url)
    funding_titles = []
    elements = driver.find_elements(By.CSS_SELECTOR, '[style]')
    for element in elements:
        if ('fontweightbold' in (re.sub(r'\W+', '',element.get_attribute("style")).lower())) and ('colorblue' in (re.sub(r'\W+', '',element.get_attribute("style")).lower())):
            funding_titles.append(element.text)
    if '\n' in ''.join(funding_titles):
        temp = funding_titles.copy()
        for title in funding_titles:
            if '\n' in title:
                temp.remove(title)
                temp = temp + title.split('\n')
                funding_titles = temp
    categories_dict[i] = ({"Category": categories[i], "Galaxy Titles": funding_titles})


# In[139]:


categories_dict


# In[ ]:




