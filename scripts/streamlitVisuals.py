#!/usr/bin/env python
# coding: utf-8

# In[59]:


# Convert to .py
get_ipython().system(
    'jupytext --to py:percent "C:\\Users\\ebroh\\BetaNYC\\School Budgets\\School-Budget-and-Allocations\\notebooks\\streamlitVisuals.ipynb"'
)


# In[1]:


import pandas as pd
from re import sub
from decimal import Decimal
import streamlit as st


def moneyToFloat(money):
    value = Decimal(sub(r"[^\d.]", "", money))
    return value


# # Total Allocations vs Budget

# In[21]:


allocations = pd.read_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\district 5\allocation_district_5.csv"
)
allocations = allocations.drop(columns=["Unnamed: 0"])
allocations["amountNum"] = allocations["amount"].apply((lambda x: moneyToFloat(x)))
# allocations


# In[22]:


totalAllocations = (
    allocations.groupby(by=["location_code", "fiscal_year"])["amountNum"]
    .sum()
    .reset_index()
)
totalAllocations = totalAllocations.rename(columns={"amountNum": "total"})
totalAllocations["type"] = "allocations"
# totalAllocations


# In[28]:


budget = pd.read_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\district 5\budget_district_5.csv"
)
budget = budget.drop(columns=["Unnamed: 0"])
budget["amountNum"] = budget["amount"].apply((lambda x: moneyToFloat(x)))
budget


# In[24]:


totalBudget = (
    budget.groupby(by=["location_code", "fiscal_year"])["amountNum"].sum().reset_index()
)
totalBudget = totalBudget.rename(columns={"amountNum": "total"})
totalBudget["type"] = "budget"
# totalBudget


# In[25]:


totals = pd.concat([totalBudget, totalAllocations])
# totals.sample(15)


# In[27]:


totalsPivot = totals.pivot(
    index=["location_code", "type"], columns=["fiscal_year"], values=["total"]
).reset_index()
# Flatten the MultiIndex columns
totalsPivot.columns = totalsPivot.columns.to_flat_index()

# Rename the columns
totalsPivot = totalsPivot.reset_index()
new_columns = ["index", "location_code", "type", "2018", "2019", "2020", "2021", "2022"]
totalsPivot.columns = new_columns
totalsPivot = totalsPivot.drop(columns="index")
totalsPivot


# # Funding by Category

# In[65]:


allocationCategories = pd.read_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\allocation_category_lookup.csv"
)
allocationCategories


# In[112]:


allocationCategories["allocation_category_group"].unique()


# In[66]:


district_5_allocation_categories = allocations.merge(
    allocationCategories,
    how="left",
    left_on="allocation_category",
    right_on="allocation_category",
)
district_5_allocation_categories


# In[69]:


funding_per_category = (
    district_5_allocation_categories.groupby(
        by=["location_code", "fiscal_year", "allocation_category_group"]
    )["amountNum"]
    .sum()
    .reset_index()
)
funding_per_category


# In[75]:


funding_per_category_pivot = funding_per_category.pivot(
    index=["location_code", "allocation_category_group"],
    columns=["fiscal_year"],
    values="amountNum",
).reset_index()
funding_per_category_pivot


# # Enrollment and FSF

# In[81]:


enrollment = pd.read_csv(
    r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\district 5\district_5_demographic_data.csv"
)
enrollment


# In[82]:


enrollment.columns


# In[91]:


def removeLeadingZero(string):
    return sub(r"^\d\d", "", string)


def year2FY(year):
    return sub(r"-\d\d$", "", year)


# In[93]:


enrollment["DBN"] = enrollment["DBN"].apply(lambda x: removeLeadingZero(x))
enrollment["fiscal_year"] = enrollment["Year"].apply(lambda x: year2FY(x))
enrollment


# In[106]:


enrollmentFinal = pd.DataFrame()
enrollmentFinal = enrollment[
    [
        "DBN",
        "fiscal_year",
        "Total Enrollment",
        "Grade 3K",
        "Grade PK (Half Day & Full Day)",
    ]
]
enrollmentFinal["3K-PreK_enrollment"] = (
    enrollmentFinal["Grade 3K"] + enrollmentFinal["Grade PK (Half Day & Full Day)"]
)
enrollmentFinal["K-5_enrollment"] = (
    enrollmentFinal["Total Enrollment"] - enrollmentFinal["3K-PreK_enrollment"]
)
enrollmentFinal = enrollmentFinal.drop(
    columns=["Grade 3K", "Grade PK (Half Day & Full Day)"]
)
enrollmentFinal


# In[136]:


pivot1 = enrollmentFinal.pivot(
    index=["DBN"], columns=["fiscal_year"], values="3K-PreK_enrollment"
).reset_index()
pivot1["Grades"] = "3K-PreK"
pivot2 = enrollmentFinal.pivot(
    index=["DBN"], columns=["fiscal_year"], values="K-5_enrollment"
).reset_index()
pivot2["Grades"] = "K-5"
enrollmentPivot = pd.concat([pivot1, pivot2])
enrollmentPivot = enrollmentPivot.rename(columns={"Grades": "Type"})
temp = funding_per_category_pivot[
    funding_per_category_pivot["allocation_category_group"].isin(
        ["Fair Student Funding", "Preschool"]
    )
]
temp = temp.rename(
    columns={
        "allocation_category_group": "Type",
        "location_code": "DBN",
        2018: "2018",
        2019: "2019",
        2020: "2020",
        2021: "2021",
    }
)
temp = temp.drop(columns=[2022])
enrollmentPivot = enrollmentPivot.drop(columns="2017")
enrollmentPivot = pd.concat([enrollmentPivot, temp])
enrollmentPivot


# # Staff vs Enrollment

# In[148]:


teaching_budget = budget[
    budget["budget_category"].isin(
        [
            "Paraprofessionals",
            "Classroom Teacher",
            "Homeroom Teacher",
            "Elementary Cluster/Quota",
            "Cluster/Quota Teacher",
        ]
    )
]
teaching_budget["budget_category"] = teaching_budget["budget_category"].replace(
    [
        "Classroom Teacher",
        "Homeroom Teacher",
        "Elementary Cluster/Quota",
        "Cluster/Quota Teacher",
    ],
    "Teacher",
)
teaching_budget.sample(10)


# In[152]:


positions_per_school = (
    teaching_budget.groupby(by=["location_code", "fiscal_year", "budget_category"])[
        "num_positions"
    ]
    .sum()
    .reset_index()
)
positions_per_school


# In[168]:


positions_per_school_pivot = positions_per_school.pivot(
    index=["location_code", "budget_category"],
    columns="fiscal_year",
    values="num_positions",
).reset_index()
positions_per_school_pivot = positions_per_school_pivot.rename(
    columns={"budget_category": "type"}
)
positions_per_school_pivot = positions_per_school_pivot.rename(
    columns={2018: "2018", 2019: "2019", 2020: "2020", 2021: "2021"}
)
positions_per_school_pivot


# In[170]:


totalEnrollment = enrollment[["DBN", "fiscal_year", "Total Enrollment"]]
totalEnrollment = totalEnrollment.rename(columns={"DBN": "location_code"})
totalEnrollmentPivot = totalEnrollment.pivot(
    index="location_code", columns="fiscal_year", values="Total Enrollment"
).reset_index()
totalEnrollmentPivot["type"] = "Total Enrollment"
staffAndEnrollment = pd.concat([totalEnrollmentPivot, positions_per_school_pivot])
staffAndEnrollment = staffAndEnrollment.drop(columns=["2017", 2022])
staffAndEnrollment


# # Budget Per Staff Member

# In[173]:


pos_and_budget = (
    teaching_budget.groupby(by=["location_code", "fiscal_year", "budget_category"])[
        "amountNum"
    ]
    .sum()
    .reset_index()
)
pos_and_budget


# In[177]:


budget_per_staff = pos_and_budget.merge(
    positions_per_school, on=["location_code", "fiscal_year", "budget_category"]
)
budget_per_staff["average_budget"] = (
    budget_per_staff["amountNum"].astype(float) / budget_per_staff["num_positions"]
)
budget_per_staff


# In[ ]:
