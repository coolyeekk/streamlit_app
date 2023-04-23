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


# Read death data from a URL and select relevant columns.
deaths_data = 'https://raw.githubusercontent.com/coolyeekk/dataset/main/linelist_deaths.csv'
df3 = pd.read_csv(deaths_data, dtype=str)

# Wrangle relevant date columns.
df3.date = pd.to_datetime(df3.date, errors='coerce').dt.date
df3.date_positive = pd.to_datetime(df3.date_positive, errors='coerce').dt.date
df3.date_dose2 = pd.to_datetime(df3.date_dose2, errors='coerce').dt.date
df3.date_dose2 = df3.date_dose2.fillna(date.today() + timedelta(1))
fvax = df3[(df3.date_positive - df3.date_dose2).dt.days > 13].copy()
fvax = fvax[fvax.date == date(2022, 4, 19)]

# Display the filtered data in the Streamlit app.
st.write('Fully Vaccinated Cases as of April 19, 2022')
st.dataframe(fvax)

from tabulate import tabulate
from matplotlib.lines import Line2D
import matplotlib.ticker as tkr

def get_age_range(age):
    if age < 18:
        return 'Under 18'
    elif age >= 18 and age < 30:
        return '18-29'
    elif age >= 30 and age < 40:
        return '30-39'
    elif age >= 40 and age < 50:
        return '40-49'
    elif age >= 50 and age < 60:
        return '50-59'
    elif age >= 60 and age < 70:
        return '60-69'
    elif age >= 70 and age < 80:
        return '70-79'
    else:
        return '80+'

def vaxStatus(date_pos, date1, date2, date3):
    if (date_pos - date3).days > 6:
        return 'boosted'
    elif (date_pos - date2).days > 13:
        return 'fullyvax'
    elif (date_pos - date1).days >= 0:
        return 'partialvax'
    else:
        return 'unvax'

def castAge(age):
    if age == -1:
        return 'missing'
    elif age < 5:
        return '0_4'
    elif age < 12:
        return '5_11'
    elif age < 18:
        return '12_17'
    elif age < 30:
        return '18_29'
    elif age < 40:
        return '30_39'
    elif age < 50:
        return '40_49'
    elif age < 60:
        return '50_59'
    elif age < 70:
        return '60_69'
    elif age < 80:
        return '70_79'
    else:
        return '80+'

def commaSep(x, pos):
    return ('{:,}'.format(x)).replace('.0', '')

deaths_data1 = 'https://raw.githubusercontent.com/coolyeekk/dataset/main/linelist_deaths.csv'
vac_age = 'https://raw.githubusercontent.com/coolyeekk/dataset/main/vax_demog_age.csv'

# Load the dataset into a dataframe
df4 = pd.read_csv('https://raw.githubusercontent.com/coolyeekk/dataset/main/linelist_deaths.csv')

# Create a new column for age ranges
df4['age_range'] = df4['age'].apply(lambda x: get_age_range(x))

# Count number of individuals in each age range
count_by_age_range = df4['age_range'].value_counts()

# The first set of numbers is taken directly from DOSM's latest release (Feb 14), with imputation only to back out the 18-29 group.
# This set of population numbers gives us an adult population of ~23.1mil

pop_age = {
'18_29' : 7067431,
'30_39' : 5636728,
'40_49' : 4021654,
'50_59' : 3030048,
'60_69' : 2050943,
'70_79' : 956402,
'80+' : 326759,
}

# This is the adjusted set, derived from supplementing national registration data with data collected via the vaccination program.
# This set of population numbers gives us an adult population of ~24mil, which drastically affects the size of the unvax population.
# Comment it out to use the first set.

pop_age = {
'18_29' : 7563410,
'30_39' : 5740871,
'40_49' : 4021654,
'50_59' : 3121816,
'60_69' : 2180719,
'70_79' : 1001044,
'80+' : 337123,
}

# Key parameters - choose timerange and whether to use date of death or date of report.
# Note: Intervals longer than 21 days are not advisable, as there may be large changes in the vax population. This requires different handling.

date_min = date.today()-timedelta(90)
date_max = date.today()-timedelta(1)
use_announced = 0

# Define a lambda function to create age ranges
df4['age_range'] = df4['age'].apply(lambda x: get_age_range(x))

# Create a new column for age ranges
df4['age_range'] = df4['age'].apply(lambda x: get_age_range(x))

# Count number of individuals in each age range
count_by_age_range = df4['age_range'].value_counts()

# Pull latest deaths linelist and wrangle
datecol = 'date_announced' if use_announced == 1 else 'date'
df5 = pd.read_csv(deaths_data1, usecols=[datecol, 'age', 'date_positive','date_dose1','date_dose2','date_dose3','brand1'])
df5 = df5.rename(columns={'date_announced':'date'})
for c in ['date','date_positive','date_dose1','date_dose2','date_dose3']: df5[c] = pd.to_datetime(df5[c],errors='coerce').dt.date
df5 = df5[(df5.date >= date_min) & (df5.date <= date_max)]


# Ensure no null vax dates (future date as placeholder), shift 14 days for Cansino, then encode vax status and age group
for c in ['date_dose1','date_dose2','date_dose3']: df5[c] = df5[c].fillna(date.today()+timedelta(1))
df5.loc[df5.brand1.isin(['Cansino']),'date_dose2'] = df5.date_dose1 + timedelta(14)
df5['status'] = df5.apply(lambda x: vaxStatus(x['date_positive'],x['date_dose1'],x['date_dose2'],x['date_dose3']),axis=1)
df5 = df5.replace(date.today()+timedelta(1),np.nan) # Remove placeholder dates
df5.age = df5.age.map(age_cat) # Encode age group

# Tabulate, keeping adults only
df5 = df5[~df5.age.isin(['0_4','5_11','12_17'])].groupby(['age','status']).size().to_frame('deaths').reset_index()
df5 = df5[~df5.status.isin(['partialvax'])].reset_index(drop=True)

# Get vax by age data and wrangle
cols_vax = ['date'] + [x + '_' + y.replace('+','') for x in ['partial','full','booster'] for y in list(pop_age.keys())]
vf = pd.read_csv(vac_age,usecols=cols_vax)
vf.columns = [x.replace('80','80+') for x in vf.columns]
vf.date = pd.to_datetime(vf.date).dt.date
vf = vf.groupby(['date']).sum().cumsum().reset_index()

# Add unvax columns, subtract partial
for c in list(pop_age.age): 
    vf['unvax_' + c] = pop_age[pop_age.age==c]['pop_age'].item() - vf['partial_' + c]
    vf['partial_' + c] = vf['partial_' + c] - vf['full_' + c]
    vf['full_' + c] = vf['full_' + c] - vf['booster_' + c]

# Shift vax columns per definitions of partial, full, boosted
for c in [x for x in vf.columns if 'partial' in x]: vf[c] = vf[c].shift(1).fillna(0).astype(int)
for c in [x for x in vf.columns if 'full' in x]: vf[c] = vf[c].shift(14).fillna(0).astype(int)
for c in [x for x in vf.columns if 'booster' in x]: vf[c] = vf[c].shift(7).fillna(0).astype(int)

# Get mean across period and transpose to merge with deaths df
vf = vf[(vf.date >= date_min) & (vf.date <= date_max)]
vf.drop(['date'], axis=1, inplace=True)
vf.loc['pop'] = vf.mean(numeric_only=True).abs()
vf = vf[vf.index == 'pop'].transpose().reset_index().rename(columns={'index':'cat'})
vf[['status','age']] = vf['cat'].str.split('_', 1, expand=True)
vf.status = vf.status.replace({'partial':'partialvax', 'full':'fullyvax', 'booster':'boosted'})
vf = vf[~vf.status.isin(['partialvax'])][['age','status','pop']].sort_values(by=['age','status']).reset_index(drop=True)

# Merge frames and compute incidence, then pivot , on=['date','status']
df5 = pd.merge(df4, vf, how='left')
df5['capita'] = df5.mortality / df5['pop'] * 100000
df5 = df5.pivot_table(index='age', columns='status', values='capita').fillna(0).reset_index()
df5.columns = ['Age','Unvaccinated','Fully Vaccinated','Boosted']
df5 = df5[['Age','Unvaccinated','Fully Vaccinated','Boosted']]

# Function for comma separator
def commaSep(x, pos): return ('{:,}'.format(x)).replace('.0', '')

# Streamlit App
st.title('Mortality rate per 100k people based on vaccination status')

# Display dataframe
st.write('Here is a sample of the mortality rate data by age group and vaccination status:')
st.write(df5)

# Display chart
plt.rcParams.update({'font.size': 8,
                     'font.family':'sans-serif',
                     'grid.linestyle':'dashed'})
plt.rcParams["figure.figsize"] = [8,7]
plt.rcParams["figure.autolayout"] = True
fig, ax = plt.subplots()
df5.plot(x='Age', y=['Unvaccinated','Fully Vaccinated','Boosted'], kind='bar', 
        color=['#FF8000','#66FFFF','#FF33FF'],
        align='center',
        width=0.7,linewidth=0.3,
        edgecolor='black',ax=ax)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True)
ax.set_axisbelow(True)
ax.legend(loc='upper center', bbox_to_anchor=(0.2, 0.95), ncol=1, labelspacing = 1.5, frameon=True, fancybox=True)
plt.xticks(rotation=0)
ax.yaxis.set_major_formatter(tkr.FuncFormatter(commaSep))
plt.tick_params(bottom=False)
plt.title('Mortality rate per 100k people based on vaccination status\n\n (data from ' + date_min.strftime('%d-%b') + ' to ' + date_max.strftime('%d-%b') + ')')
plt.xlabel('')
plt.ylabel('')
plt.tight_layout()
st.pyplot(fig)
