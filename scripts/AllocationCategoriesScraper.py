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


# In[2]:


chrome_options = webdriver.ChromeOptions()
# save any files in the current working directory
# prefs = {'download.default_directory' : os.getcwd()}
# chrome_options.add_argument("--headless")
# chrome_options.add_experimental_option('prefs', prefs)
service = ChromeService(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)


# In[3]:


script = """
return ['span', 'b', 'strong', 'tr td', 'ul li', ].reduce((nodelist, selector) => [...nodelist, ...document.querySelectorAll(selector)] , [])
.filter(e => 
    ['blue','rgb(0, 0, 255)'].includes(getComputedStyle(e).getPropertyValue('color')) && (['bold','bolder'].includes(getComputedStyle(e).getPropertyValue('font-weight')) || getComputedStyle(e).getPropertyValue('font-weight') >= 500)
).map(e => e.innerText)
"""


# In[4]:


def getAllocationCategories(year, driver):
    # Navigate to the memorandums page for the given year
    url = "https://infohub.nyced.org/reports/financial/financial-data-and-reports/school-allocation-memorandums"
    year = str(year)
    driver.get(url)
    link2memorandums = ""
    elements = driver.find_elements(By.CSS_SELECTOR, 'a[target="_blank"]')
    for element in elements:
        if year in element.text:
            link2memorandums = element.get_attribute("href")
            break
    driver.get(link2memorandums)

    # Go to the 	School Allocation Memorandums sorted numerically
    driver.find_element(By.XPATH, "//*[contains(text(), 'SAMs by Numbers')]").click()

    # Make a list of all the links to allocation memorandums and category titles
    url_prefix = link2memorandums.split("am_")[0]
    urls = []
    categories = []
    page = requests.get(driver.current_url)
    soup = BeautifulSoup(page.text, "html.parser")
    table = soup.find("table")

    ran = False

    for row in table:
        try:
            # FSF has multiple entries but we only need the memorandum
            for a in row.find_all("a", href=True):
                if a.text == "Fair Student Funding Memorandum":
                    urls.append(url_prefix + a["href"])
                    categories.append(a.text)
                # After 'Allocation Summary by District' marks the start of memorandum links
                if "Allocation Summary by District" in a.text:
                    ran = True
                    continue
                # If you have passed 'Allocation Summary by District' start to save the category titles and links
                if ran:
                    if a["href"].startswith("http"):
                        urls.append(a["href"])
                    else:
                        urls.append(url_prefix + a["href"])
                    categories.append(a.text)
        except:
            continue

    # Formatting the titles
    for i, category_title in enumerate(categories):
        categories[i] = re.sub("\\r|\\t|\\n", "", category_title)

    # List of dictionaries with allocation titles and galaxy listing
    categories_list = []
    sam_text = []

    # Add the galaxy listings for every allocation title
    for i, url in enumerate(urls):
        driver.get(url)
        funding_titles = driver.execute_script(script)
        res = requests.get(url)

        # Initialize the object with the document
        soup = BeautifulSoup(res.content, "html.parser")

        # Get the whole body tag
        tag = soup.body
        body = ""
        # Print each string recursively
        for string in tag.strings:
            body = body + "\n\n" + string

        categories_list.append(
            {"Category": categories[i], "Galaxy Titles": funding_titles, "Body": body}
        )

    return categories_list


# In[7]:


allocationCategories2021 = getAllocationCategories(2021, driver)
allocationCategories2021


# In[10]:


allocationCategories2020 = getAllocationCategories(2020, driver)
allocationCategories2020


# In[5]:


allocationCategories2022, sams2022 = getAllocationCategories(2022, driver)


# In[6]:


allocationCategories2022


# In[8]:


expanded_data = []
for item in allocationCategories2022:
    for title in item["Galaxy Titles"]:
        expanded_row = {
            "Category": item["Category"],
            "Galaxy Titles": title,
            "Body": item["Body"],
        }
        expanded_data.append(expanded_row)

# Convert the expanded_data list to a DataFrame
df = pd.DataFrame(expanded_data)
df


# In[9]:


df.to_csv("sams2022.csv")


# In[208]:


district_5_allocations = pd.read_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\district 5\allocation_district_5.csv"
)
district_5_allocations


# In[209]:


M125_allocations = district_5_allocations[
    district_5_allocations["location_code"] == "M125"
]
M125_allocations


# In[274]:


M125_2022 = M125_allocations[M125_allocations["fiscal_year"] == 2022]
M125_2022 = M125_2022.drop(columns=("Unnamed: 0"))
M125_allocation_categories = M125_2022["allocation_category"].unique()
all_2022_categories = []
for i in allocationCategories2022:
    all_2022_categories = all_2022_categories + i["Galaxy Titles"]
overlap = [x for x in M125_allocation_categories if x not in all_2022_categories]
overlap


# In[289]:


M125_2021 = M125_allocations[M125_allocations["fiscal_year"] == 2021]
M125_2021 = M125_2021.drop(columns=("Unnamed: 0"))
M125_allocation_categories = M125_2021["allocation_category"].unique()
all_2021_categories = []
for i in allocationCategories2021:
    all_2021_categories = all_2021_categories + i["Galaxy Titles"]
overlap = [x for x in M125_allocation_categories if x not in all_2021_categories]
overlap


# In[288]:


M125_2020 = M125_allocations[M125_allocations["fiscal_year"] == 2020]
M125_2020 = M125_2020.drop(columns=("Unnamed: 0"))
M125_allocation_categories = M125_2020["allocation_category"].unique()
all_2020_categories = []
for i in allocationCategories2020:
    all_2020_categories = all_2020_categories + i["Galaxy Titles"]
overlap = [x for x in M125_allocation_categories if x not in all_2021_categories]
overlap


# In[282]:


district_5_allocations = district_5_allocations.drop(columns="Unnamed: 0")


# In[298]:


district_5_allocations_2022 = district_5_allocations["allocation_category"][
    district_5_allocations["fiscal_year"] == 2022
].unique()
district_5_allocations_2022


# In[27]:


memorandum_lookup = pd.DataFrame()
for memorandum_category in allocationCategories2022:
    for galaxy_title in memorandum_category["Galaxy Titles"]:
        memorandum_lookup = pd.concat(
            [
                memorandum_lookup,
                pd.DataFrame(
                    {
                        "memorandum_category": [memorandum_category["Category"]],
                        "galaxy_title": [galaxy_title],
                        "body": [memorandum_category["Body"]],
                    }
                ),
            ],
            ignore_index=True,
        )
memorandum_lookup


# In[29]:


memorandum_lookup.to_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\memorandum_lookups\memorandum_lookup2022_v2.csv"
)


# In[ ]:


# Added pre-commit file test (part 3)


# In[ ]:
