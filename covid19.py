import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import datetime
from datetime import date, timedelta

# Function to get data from S3
@st.cache(persist=True)
def get_data_from_s3(path):
    return pd.read_parquet(path)

@st.cache(persist=True)
def get_geo_data():
    url_param_geo = 'https://raw.githubusercontent.com/coolyeekk/dataset/main/param_geo.csv'
    geo = pd.read_csv(url_param_geo)
    idxd_district = dict(zip(geo.idxd, geo.district))
    idxs_state = dict(zip(geo.idxs, geo.state))
    district_state = dict(zip(geo.district, geo.state))
    return idxd_district, idxs_state, district_state

# Get data from S3
path_cases = 'https://moh-malaysia-covid19.s3.ap-southeast-1.amazonaws.com/linelist_cases.parquet'
df = get_data_from_s3(path_cases)

# Get district, state, and cases
idxd_district, idxs_state, district_state = get_geo_data()
df['state'] = df.state.map(idxs_state)
df['district'] = df.district.map(idxd_district)
df = df[~df.district.isnull()].copy()
df.date = pd.to_datetime(df.date)
df['cases'] = 1

df = df.groupby(['date','district'])\
    .sum()\
    .unstack(fill_value=0)\
    .asfreq('D', fill_value=0)\
    .stack()\
    .sort_index(level=1)\
    .reset_index()
df.date = df.date.dt.date
df['state'] = df.district.map(district_state)
df = df[['date','state','district','cases']]
df = df.sort_values(by=['date','state','district']).reset_index(drop=True)

# Create Streamlit app
st.title("Covid-19 Cases by State and District in Malaysia")

# Select date
dates = np.sort(df['date'].unique())[::-1]
selected_date = st.selectbox("Select Date", dates)

# Filter data by date
df_filtered = df[df['date'] == selected_date]

# Show data
st.write(df_filtered)



# Read case data from a URL and select relevant columns (date, state, cases_new).
cases_state1 = 'https://raw.githubusercontent.com/coolyeekk/dataset/main/cases_state.csv'
df2 = pd.read_csv(cases_state1, usecols=['date','state','cases_new'], parse_dates=['date'])

# Replace state codes in the dataframe with their corresponding names using mergeKV dictionary.
mergeKV = {'Selangor': 'Sel & WP', 'W.P. Kuala Lumpur': 'Sel & WP', 'W.P. Putrajaya': 'Sel & WP'}
df2.state = df2.state.replace(mergeKV)

# Group by date and state, and calculate the sum of new cases for each group. Then reset the index of the resulting dataframe.
df2 = df2.groupby(['date','state']).sum().reset_index()

# Filter by cases from April 19, 2021 onwards (start of Phase 2 vaccination).
df2 = df2[df2.date.dt.date >= pd.Timestamp('2021-04-19').date()]

# Define a helper function to check if the resulting dataframe includes all states.
def df2IsComplete(df2):
    odf = df2.copy()
    dff = df2.groupby(['date', 'state']).sum().unstack(fill_value=0).asfreq('D', fill_value=0).stack().sort_index(level=1).reset_index().sort_values(by=['date', 'state'])
    dff.date = dff.date.dt.date
    return len(odf) == len(dff)

# Check if the resulting dataframe includes all states.
if not df2IsComplete(df2):
    st.warning('Not all states are included in the data.')

# Create a chart showing COVID-19 case trends by state.
states = list(df2.state.unique())
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams.update({'font.size': 16})
figure, axes = plt.subplots(4,4, figsize=(30,30), sharey=True)
figure.set_size_inches([15,15], forward=True)
figure.suptitle('COVID-19 Case Trends')
axe = axes.ravel()
i = 0
for s in states:
    temp = df2.copy()
    temp = temp[temp.state == s]
    temp.cases_new = (temp.cases_new - temp.cases_new.min()) / (temp.cases_new.max() - temp.cases_new.min()) * 100
    temp['cases_new_ma'] = temp['cases_new'].rolling(window=7).mean()
    temp = temp.dropna(how='any')
    temp['cases_new'].plot(ax=axe[i], legend=None, color='black', linewidth=0.5, alpha=0.5)
    temp['cases_new_ma'].plot(ax=axe[i], legend=None, color='black')
    axe[i].set_title(s)
    i += 1
plt.setp(axes, xticks=[], yticks=[])
figure.tight_layout()
figure.subplots_adjust(top=0.88)

# Display the chart in the Streamlit app.
st.pyplot(figure)