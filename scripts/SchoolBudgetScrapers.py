#!/usr/bin/env python
# coding: utf-8

# In[3]:


#install packages
get_ipython().system('pip install beautifulsoup4 selenium webdriver-manager pandas requests')


# In[51]:


from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import numpy as np
import glob
import time
import re


# In[33]:


chrome_options = webdriver.ChromeOptions()
#save any files in the current working directory
prefs = {'download.default_directory' : os.getcwd()}
chrome_options.add_experimental_option('prefs', prefs)
service = ChromeService(executable_path=ChromeDriverManager().install())


# In[61]:


BUDGET_TYPES = {
    'budget': {
        'url': 'https://www.nycenet.edu/offices/d_chanc_oper/budget/dbor/galaxy/galaxybudgetsummaryto/default.aspx'
    },
    'allocation': {
        'url': 'https://www.nycenet.edu/offices/d_chanc_oper/budget/dbor/galaxy/galaxyallocation/default.aspx'
    }
}

def openBudgetSite(driver, school_code, fiscal_year, budgetType):
    # go to url
    url = BUDGET_TYPES.get(budgetType, {}).get('url')
    if not url: raise ValueError(f'Budget or Allocation value must be either {BUDGET_TYPES.keys()}')
    driver.get(url)
                         
    # type school code
    element = driver.find_element(By.XPATH,'//*[@id="School_Code"]')
    element.send_keys(school_code)

    # select fiscal year in drop down
    x = driver.find_element(By.XPATH,'//*[@id="Fiscal_Year"]')
    drop=Select(x)
    drop.select_by_visible_text(fiscal_year)

    # submit
    driver.find_element(By.XPATH,'//*[@id="Enter"]').click()

    try:
        element = driver.find_element(By.XPATH,'//*[@id="message"]/div[1]/div[3]/h2/a')
        # check if codes match
        driver_school_code = re.search('\d{2}(.{1}\d{3})',element.text).group(1)
        return school_code == driver_school_code
    except Exception as e:    
        #[on_true] if [expression] else [on_false] 
        print(e.message) if hasattr(e, 'message') else print(e)
        return False


# In[77]:


def allocationPageScraper(driver, school_code, fiscal_year):
    list_of_dfs = pd.read_html(driver.page_source)
    df = pd.concat(list_of_dfs, ignore_index=True)

    #rename columns
    df.columns = ['allocation_category', 'amount']
    
    #remove rows with total
    #df = df[df["allocation_category"].str.contains("total", case = False)==False]
    df = df[~df['allocation_category'].str.contains("Grand Total")]
    
    #add id columns
    final_df['location_code'] = school_code
    final_df['fiscal_year'] = fiscal_year
    return final_df


# In[83]:


def budgetPageScraper(driver, school_code, fiscal_year):
    section_titles = driver.find_elements(By.CLASS_NAME , 'TO_Section')
    list_of_dfs = pd.read_html(driver.page_source)
    final_df = pd.DataFrame()
    
    COLUMN_OPITONS = {
        2: ['budget_assignment','amount'],
        3: ['budget_assignment','num_positions','amount'],
        4: ['budget_assignment','service_type','num_positions','amount']
    }
    
    for i, df in enumerate(list_of_dfs):
        #rename columns
        new_columns = COLUMN_OPITONS[len(df.columns)]
        df.columns = new_columns
        
        #add budget_category context (otps, per session , per diem, etc)
        df['budget_category'] = section_titles[i].text
        
        #todo: drop total 
        
        
        final_df = pd.concat([final_df, df])
        
    #remove rows with total
    df = df[~df['budget_assignment'].str.contains("Grand Total")]
    
    #add id columns
    final_df['location_code'] = school_code
    final_df['fiscal_year'] = fiscal_year
   
            
    return final_df


# In[47]:


school_code = 'M125'
fiscal_year = '2022'
driver = webdriver.Chrome(service = service, options=chrome_options)


# In[78]:


if openBudgetSite(driver, school_code, fiscal_year, 'allocation'):
    df = allocationPageScraper(driver, school_code, fiscal_year)


# In[84]:


if openBudgetSite(driver, school_code, fiscal_year, 'budget'):
    df = budgetPageScraper(driver, school_code, fiscal_year)

