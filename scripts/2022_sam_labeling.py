import sam_funding_analysis as sfa
import pandas as pd
import re

sams2022 = pd.read_csv(r"C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\memorandum_lookups\sams2022.csv")
sams2022

df = sams2022.drop(columns = ['Unnamed: 0', 'Galaxy Titles']).drop_duplicates().reset_index(drop = True)

# +
#test_df = df.head(5)

# +
#test_df
# -

df1 = pd.DataFrame()
for i,row in df.iterrows():
    funding_source, confidence, responses = sfa.get_funding_source(row['Body'])
    new_row = {
        'Category':row['Category'],
        'Body':row['Body'],
        'funding_source': funding_source,
        'confidence': confidence,
        'responses': responses
    }
    df1 = pd.concat([df1, pd.DataFrame(new_row)])

df1.reset_index(drop = True)

df2 = df1.drop(columns = ['Body'])

df2.to_csv(r'C:\Users\ebroh\BetaNYC\School Budgets\School-Budget-and-Allocations\data\2022_funding_sources.csv')

df1


