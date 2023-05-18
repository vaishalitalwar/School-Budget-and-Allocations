#!/usr/bin/env python
# coding: utf-8

# In[221]:


import pandas as pd
import numpy as np
import re


# In[222]:


categories = pd.read_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\memorandum_lookups\memorandum_lookup2022.csv"
)
categories = categories.drop(columns=["Unnamed: 0"])
categories


# In[223]:


categories2 = pd.read_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\memorandum_lookups\memorandum_lookup2022_v2.csv"
)
descriptions = categories2["body"]


# In[224]:


categories2 = categories2.drop(columns=["Unnamed: 0", "galaxy_title"]).drop_duplicates()
categories2


# In[225]:


df = pd.DataFrame()

for title in missing_titles:
    for index, row in categories2.iterrows():
        if title.lower() in row["body"].lower():
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        {
                            "galaxy_title": [title],
                            "memorandum_category": row["memorandum_category"],
                        }
                    ),
                ],
                ignore_index=True,
            )

df


# In[226]:


categories = pd.concat([categories, df])
categories["join"] = (
    categories["galaxy_title"].str.strip().str.lower().str.replace("\W", "")
)
categories


# In[227]:


district_5_allocations = pd.read_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\district 5\allocation_district_5.csv"
)
district_5_allocations = district_5_allocations[
    district_5_allocations["fiscal_year"] == 2022
]
district_5_allocations["join"] = (
    district_5_allocations["allocation_category"]
    .str.strip()
    .str.lower()
    .str.replace("\W", "")
)
district_5_allocations


# In[228]:


final = district_5_allocations.merge(
    categories, left_on="join", right_on="join", how="left"
)
final


# In[230]:


final = final.drop(columns=["Unnamed: 0", "galaxy_title", "join"])
final


# In[231]:


final["memorandum_category"] = final.apply(
    lambda x: "FSF Other"
    if ("FSF" in x["allocation_category"] and str(x["memorandum_category"]) == "nan")
    else x["memorandum_category"],
    axis=1,
)
final["memorandum_category"] = final.apply(
    lambda x: re.search("Title\s[\w\d]+", x["allocation_category"]).group(0) + " Other"
    if (
        (re.search("Title\s[\w\d]+", str(x["allocation_category"])) is not None)
        and (str(x["memorandum_category"]) == "nan")
    )
    else x["memorandum_category"],
    axis=1,
)
final["memorandum_category"] = final.apply(
    lambda x: "Smart Schools Bond Act (2021)"
    if x["allocation_category"] == "Rollover Smart Schools Bond Act"
    else x["memorandum_category"],
    axis=1,
)
final["memorandum_category"] = final.apply(
    lambda x: "NYSTL Other"
    if (
        (re.search("NYSTL", str(x["allocation_category"])) is not None)
        and (str(x["memorandum_category"]) == "nan")
    )
    else x["memorandum_category"],
    axis=1,
)
final


# In[232]:


final[final["memorandum_category"].fillna("N/A").str.contains("Other")][
    "memorandum_category"
].value_counts()


# In[233]:


missing_titles = final[final["memorandum_category"].isnull()][
    "allocation_category"
].unique()


# In[234]:


missing_titles


# In[235]:


included_titles = final[~final["memorandum_category"].isnull()][
    "allocation_category"
].unique()


# In[236]:


frequency = final["allocation_category"].value_counts().reset_index()


# In[237]:


frequency


# In[238]:


frequency[frequency["index"].isin(missing_titles)]


# In[92]:


frequency[frequency["index"].isin(included_titles)]


# In[ ]:


len(final[final["memorandum_category"].isnull()]["allocation_category"].unique())


# In[116]:


str(final[final["memorandum_category"].isnull()]["memorandum_category"][29])


# In[65]:


final[final["allocation_category"].fillna("0").str.contains("TL RS IEP T")]


# In[60]:


categories[
    categories["galaxy_title"].fillna("0").str.contains("TL RS IEP")
].reset_index()["galaxy_title"][0]


# In[32]:


"ARPA Academic Recovery Para Summer Rising" == "ARPA Academic Recovery Para Summer Rising	"


# In[ ]:
