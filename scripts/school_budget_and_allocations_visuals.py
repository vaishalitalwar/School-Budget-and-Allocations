import streamlit as st
import pandas as pd
import altair as alt
import re
import numpy as np

def moneyToFloat(money):
    value = float(re.sub(r'[^\d.]', '', money))
    return value

allocations = pd.read_csv(r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\district 5\allocation_district_5.csv")
allocations = allocations.drop(columns = ['Unnamed: 0'])
allocations['amountNum'] = allocations['amount'].apply((lambda x: moneyToFloat(x)))

budget = pd.read_csv(r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\district 5\budget_district_5.csv")
budget = budget.drop(columns = ['Unnamed: 0'])
budget['amountNum'] = budget['amount'].apply((lambda x: moneyToFloat(x)))

allocationCategories = pd.read_csv(r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\allocation_category_lookup.csv")


# Add the enrollmentPivot DataFrame
# Replace this with the actual DataFrame you have
enrollment = pd.read_csv(r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\district 5\district_5_demographic_data.csv")

# Filter for school_code
unique_school_codes = budget["location_code"].unique()
default_value = int(np.where(unique_school_codes == "M125")[0][0])
school_code = st.selectbox("Select School Code", unique_school_codes, index = default_value)

def removeLeadingZero(string):
    return(re.sub(r'^\d\d', '', string))

def year2FY(year):
    return(re.sub(r'-\d\d$', '', year))


##############################

totalBudget = budget.groupby(by=['location_code', 'fiscal_year'])['amountNum'].sum().reset_index()
totalBudget = totalBudget.rename(columns = {'amountNum': 'total'})
totalBudget['type'] = 'budget'



totalAllocations = allocations.groupby(by=['location_code', 'fiscal_year'])['amountNum'].sum().reset_index()
totalAllocations = totalAllocations.rename(columns = {'amountNum': 'total'})
totalAllocations['type'] = 'allocations'

totals = pd.concat([totalBudget, totalAllocations])
#totals.sample(15)

totalsPivot = totals.pivot(index = ['location_code', 'type'], columns = ['fiscal_year'], values = ['total']).reset_index()
# Flatten the MultiIndex columns
totalsPivot.columns = totalsPivot.columns.to_flat_index()

# Rename the columns
totalsPivot = totalsPivot.reset_index()
new_columns = ['index', 'location_code', 'type', '2018', '2019', '2020', '2021', '2022']
totalsPivot.columns = new_columns
totalsPivot =  totalsPivot.drop(columns = 'index')
#totalsPivot


# Pivot DataFrame to have years as index
df = totalsPivot.melt(id_vars=["location_code", "type"], var_name="year", value_name="amount")
#df["year"] = df["year"].astype(int)
df["amount"] = df["amount"].astype(float)

# Streamlit app
st.title("School Budget and Allocations")

filtered_df = df[df["location_code"] == school_code]


# Create line chart with dot markers
line = (
    alt.Chart(filtered_df)
    .mark_line()
    .encode(
        x=alt.X("year:O"),
        y=alt.Y("amount:Q"),
        color="type:N",
    )
)

dots = (
    alt.Chart(filtered_df)
    .mark_circle(size=100)
    .encode(
        x=alt.X("year:O"),
        y=alt.Y("amount:Q"),
        color="type:N",
        tooltip=["type", "year", "amount"],
    )
)

budgets_allocations_chart = (line + dots).properties(width=600, height=400, title="Budget vs Allocations")

# Display table with corresponding values
st.subheader(f"Data for School Code {school_code}")
#st.write(filtered_df.pivot_table(index="year", columns="type", values="amount").reset_index())

st.altair_chart(budgets_allocations_chart, use_container_width=True)

#######################################

st.title("Funding per Category")

district_5_allocation_categories = allocations.merge(allocationCategories, how = 'left', left_on = 'allocation_category', right_on = 'allocation_category')
funding_per_category = district_5_allocation_categories.groupby(by = ['location_code', 'fiscal_year', 'allocation_category_group'])['amountNum'].sum().reset_index()
funding_per_category_pivot = funding_per_category.pivot(index = ['location_code', 'allocation_category_group'], columns = ['fiscal_year'], values = 'amountNum').reset_index()

funding_per_category_filtered = funding_per_category[funding_per_category['location_code'] == school_code]

funding_per_category_chart = (
    alt.Chart(funding_per_category_filtered)
    .mark_bar()
    .encode(
        x=alt.X("fiscal_year:O", title="Fiscal Year"),
        y=alt.Y("amountNum:Q", title="Funding Amount"),
        color=alt.Color("allocation_category_group:N", title="Allocation Category"),
        tooltip=["allocation_category_group", "fiscal_year", "amountNum"],
    )
    .properties(width=600, height=400, title="Funding per Allocation Category")
)

st.altair_chart(funding_per_category_chart, use_container_width=True)



######################################

enrollment['DBN'] = enrollment['DBN'].apply(lambda x: removeLeadingZero(x))
enrollment['fiscal_year'] = enrollment['Year'].apply(lambda x: year2FY(x))


enrollmentFinal = pd.DataFrame()
enrollmentFinal = enrollment[['DBN','fiscal_year', 'Total Enrollment', 'Grade 3K', 'Grade PK (Half Day & Full Day)']]
enrollmentFinal['3K-PreK_enrollment'] = enrollmentFinal['Grade 3K'] + enrollmentFinal['Grade PK (Half Day & Full Day)']
enrollmentFinal['K-5_enrollment'] = enrollmentFinal['Total Enrollment'] - enrollmentFinal['3K-PreK_enrollment']
enrollmentFinal = enrollmentFinal.drop(columns = ['Grade 3K', 'Grade PK (Half Day & Full Day)'])
pivot1 = enrollmentFinal.pivot(index = ['DBN'], columns = ['fiscal_year'], values = '3K-PreK_enrollment').reset_index()
pivot1['Grades'] = '3K-PreK Enrollment'
pivot2 = enrollmentFinal.pivot(index = ['DBN'], columns = ['fiscal_year'], values = 'K-5_enrollment').reset_index()
pivot2['Grades'] = 'K-5 Enrollment'
enrollmentPivot = pd.concat([pivot1, pivot2])
enrollmentPivot = enrollmentPivot.rename(columns = {'Grades':'Type'})
temp = funding_per_category_pivot[funding_per_category_pivot['allocation_category_group'].isin(['Fair Student Funding', 'Preschool'])]
temp = temp.rename(columns = {'allocation_category_group': 'Type', 'location_code': 'DBN', 2018:'2018', 2019:'2019', 2020:'2020', 2021:'2021'})
temp = temp.drop(columns = [2022])
enrollmentPivot = enrollmentPivot.drop(columns = '2017')
enrollmentPivot = pd.concat([enrollmentPivot, temp])

# Melt the DataFrame to have years as rows
enrollment_melted = enrollmentPivot.melt(
    id_vars=["DBN", "Type"],
    var_name="year",
    value_name="value",
)
enrollment_melted["year"] = enrollment_melted["year"].astype(int)

# Create calculated columns for adjusted values
enrollment_melted["value_adjusted"] = enrollment_melted.apply(
    lambda row: row["value"] / 10000 if row["Type"] in ["Fair Student Funding", "Preschool"] else row["value"],
    axis=1
)


def update_type_and_value(row):
    if row["Type"] == "Preschool":
        return "Preschool Funding / 10,000", row["value"] / 10000
    elif row["Type"] == "Fair Student Funding":
        return "Fair Student Funding / 10,000", row["value"] / 10000
    else:
        return row["Type"], row["value"]

enrollment_melted[["Type", "value"]] = enrollment_melted.apply(update_type_and_value, axis=1, result_type="expand")

filtered_enrollment_melted = enrollment_melted[enrollment_melted["DBN"] == school_code]


# Create a list of line types
line_types = ["3K-PreK Enrollment", "K-5 Enrollment", "Fair Student Funding / 10,000", "Preschool Funding / 10,000"]

# Create the base chart
base = alt.Chart(filtered_enrollment_melted).encode(
    x=alt.X("year:O", scale=alt.Scale(zero=False), axis=alt.Axis(format="d")),
    y="value_adjusted:Q",
    color="Type:N",
    tooltip=["DBN", "Type", "year", "value"],
)

# Create the multi-line chart
multiline_chart = alt.layer(
    *[base.transform_filter(alt.datum["Type"] == line_type).mark_line() for line_type in line_types]
).properties(width=600, height=400, title="Enrollment and Funding by Type")



# Display multi-line chart in Streamlit
st.altair_chart(multiline_chart, use_container_width=True)

#########################################

teaching_budget = budget[budget['budget_category'].isin(['Paraprofessionals', 'Classroom Teacher', 'Homeroom Teacher', 'Elementary Cluster/Quota', 'Cluster/Quota Teacher'])]
teaching_budget['budget_category'] = teaching_budget['budget_category'].replace(['Classroom Teacher', 'Homeroom Teacher', 'Elementary Cluster/Quota', 'Cluster/Quota Teacher'], 'Teacher')

positions_per_school = teaching_budget.groupby(by = ['location_code', 'fiscal_year', 'budget_category'])['num_positions'].sum().reset_index()

positions_per_school_pivot = positions_per_school.pivot(index = ['location_code', 'budget_category'], columns = 'fiscal_year', values = 'num_positions').reset_index()
positions_per_school_pivot = positions_per_school_pivot.rename(columns = {'budget_category': 'type'})
positions_per_school_pivot = positions_per_school_pivot.rename(columns = {2018:'2018', 2019:'2019', 2020:'2020', 2021:'2021'})

totalEnrollment = enrollment[['DBN','fiscal_year', 'Total Enrollment']]
totalEnrollment = totalEnrollment.rename(columns = {'DBN': 'location_code'})
totalEnrollmentPivot = totalEnrollment.pivot(index = 'location_code', columns = 'fiscal_year', values = 'Total Enrollment').reset_index()
totalEnrollmentPivot['type'] = 'Total Enrollment'
staffAndEnrollment = pd.concat([totalEnrollmentPivot,positions_per_school_pivot])
staffAndEnrollment = staffAndEnrollment.drop(columns = ['2017', 2022])

df = staffAndEnrollment.melt(id_vars=["location_code", "type"], var_name="year", value_name="amount")

# Modify Total Enrollment values
df.loc[df["type"] == "Total Enrollment", "amount"] /= 10

# Streamlit app
st.title("Staff and Enrollment")

# Filter for school_code
filtered_df = df[df["location_code"] == school_code]

# Create line chart
staff_and_enrollment_chart = (
    alt.Chart(filtered_df)
    .mark_line()
    .encode(
        x="year:O",
        y="amount:Q",
        color="type:N",
        tooltip=["type", "amount"],
    )
    .properties(width=600, height=400, title="Total Enrollment / 10, Teacher, and Paraprofessionals")
)

st.altair_chart(staff_and_enrollment_chart, use_container_width=True)

##############################################

pos_and_budget = teaching_budget.groupby(by = ['location_code', 'fiscal_year', 'budget_category'])['amountNum'].sum().reset_index()

budget_per_staff = pos_and_budget.merge(positions_per_school, on = ['location_code','fiscal_year','budget_category'])
budget_per_staff['average_budget'] = budget_per_staff['amountNum'].astype(float)/budget_per_staff['num_positions']

budget_per_staff_melted = budget_per_staff.melt(id_vars=["location_code", "fiscal_year", "budget_category"], var_name="metric", value_name="value")
budget_per_staff_melted_filtered = budget_per_staff_melted[budget_per_staff_melted["location_code"] == school_code]
st.title("Average Budget per Staff")

budget_per_staff_chart = (
    alt.Chart(budget_per_staff_melted_filtered)
    .mark_bar()
    .encode(
        x=alt.X("budget_category:N", title="Budget Category"),
        y=alt.Y("value:Q", title="Average Budget"),
        color=alt.Color("budget_category:N", title="Staff Type"),
        column=alt.Column("fiscal_year:O", title="Fiscal Year"),
        tooltip=["budget_category", "fiscal_year", "value"],
    )
    .properties(width=600, height=400, title="Average Budget for Teachers and Paraprofessionals")
)


st.altair_chart(budget_per_staff_chart, use_container_width=True)