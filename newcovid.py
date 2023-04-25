import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from plotly.subplots import make_subplots
import json
import requests


df = pd.read_csv("https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/clusters.csv")
df.drop(["cluster", "district", "date_announced","date_last_onset", "category", "status",
          "tests", "icu", "summary_bm", "summary_en"], axis=1, inplace=True)
df = df[df["cases_total"] != 0]

st.set_page_config(page_title='Streamlit Dashboard',
                   layout='wide',
                   page_icon='💹')

st.markdown("<h1 style='text-align: center; color: red;'>Covid-19 Cases by State and District in Malaysia</h1>",
            unsafe_allow_html=True)

st.markdown("---")

st.markdown("<p style='text-align: justify;'>hi</p>", unsafe_allow_html=True)

st.markdown("<h4 style='text-align: justify; color: blue;'>This dashboard is an effort to analyze the cumulative data of New Cases, Active Cases, Deaths and Recovered over time.</h4>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>CASES ACROSS Malaysia</h2>",
            unsafe_allow_html=True)
now = datetime.now().strftime("%d/%m/%Y")

st.markdown(f"<p style='text-align: center;'>Current Date: {now}</p>", unsafe_allow_html=True)

# kpi 1

con, rec, det, act = st.beta_columns(4)

with con:
    st.markdown("<h3 style='text-align: center;'>New Cases</h3>",
                unsafe_allow_html=True)
    num1 = df['cases_new'][0]
    st.markdown(
        f"<h2 style='text-align: center; color: blue;'>{num1}</h2>", unsafe_allow_html=True)

with rec:
    st.markdown("<h3 style='text-align: center;'>Recovered Cases</h3>",
                unsafe_allow_html=True)
    num2 = df['recovered'].sum()
    st.markdown(
        f"<h2 style='text-align: center; color: green;'>{num2}</h2>", unsafe_allow_html=True)

with det:
    st.markdown("<h3 style='text-align: center;'>Total Deaths</h3>",
                unsafe_allow_html=True)
    num3 = df['deaths'].sum()
    st.markdown(
        f"<h2 style='text-align: center; color: red;'>{num3}</h2>", unsafe_allow_html=True)

with act:
    st.markdown("<h3 style='text-align: center;'>Total Cases</h3>",
                unsafe_allow_html=True)
    num3 = df['cases_total'].sum()
    st.markdown(
        f"<h2 style='text-align: center; color: orange;'>{num3}</h2>", unsafe_allow_html=True)

st.markdown("---")

# kpi2

df1 = pd.read_csv(
    "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/clusters.csv")

st.markdown("<h2 style='text-align: center;'>Visualizing Total Cases & ICU & Deaths</h2>",
            unsafe_allow_html=True)

first_chart, second_chart = st.beta_columns(2)

with first_chart:
    fig = px.line(df1, x=pd.to_datetime(df1["date_announced"]).dt.strftime('%b %d %Y'), 
              y=["cases_active", "recovered"], 
              title="Total active cases and recovered",
              color_discrete_sequence=["blue", "green"])

    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)

with second_chart:
    fig = px.line(df1, x=pd.to_datetime(df1["date_announced"]).dt.strftime('%b %d %Y'),
              y=["tests", "cases_total"],
              title="Total tests and cases",
              color_discrete_sequence=["blue", "green"])

    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# kpi3

# Read data from MoH Malaysia dataset
df_state = pd.read_csv("https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv")

# Define options for state dropdown menu
state_options = sorted(list(df_state['state'].unique()))

# Create state dropdown menu
state_selected = st.selectbox('Select a state:', state_options)

# Filter data for the selected state
state_data = df_state[df_state['state'] == state_selected]

# Group data by date and calculate the sum of active cases, new cases, and recovered cases
date_data = state_data.groupby('date').sum().reset_index()

# Create plot data for each case type
active_cases = go.Scatter(x=date_data['date'], y=date_data['cases_active'], name='Active Cases')
new_cases = go.Scatter(x=date_data['date'], y=date_data['cases_new'], name='New Cases')
recovered_cases = go.Scatter(x=date_data['date'], y=date_data['cases_recovered'], name='Recovered Cases')

# Create figure layout and add plot data
fig = go.Figure(data=[active_cases, new_cases, recovered_cases])
fig.update_layout(title=f"COVID-19 Cases in {state_selected}", xaxis_title="Date", yaxis_title="Number of Cases")

# Display the plot
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)



# Pie Chart
# Read data from MoH Malaysia dataset
df_clusters = pd.read_csv("https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/clusters.csv")

# Group data by state and calculate the sum of cases, recoveries, deaths, and new cases
state_grouped = df_clusters.groupby('district').agg({'cases_total': 'sum', 'recovered': 'sum', 'deaths': 'sum', 'cases_active': 'sum'}).reset_index()
state_grouped = state_grouped.sort_values('cases_total', ascending=False).head(5)

# Create pie chart data for each case type
state_grouped['district_short'] = state_grouped['district'].str.replace(' ', '<br>')
total_cases = go.Pie(labels=state_grouped['district'], values=state_grouped['cases_total'], name='Total Cases')
total_recovered = go.Pie(labels=state_grouped['district'], values=state_grouped['recovered'], name='Total Recovered')
total_deaths = go.Pie(labels=state_grouped['district'], values=state_grouped['deaths'], name='Total Deaths')
active = go.Pie(labels=state_grouped['district'], values=state_grouped['cases_active'], name='Active Cases')

# Display Total Cases Pie Chart
with st.beta_container():
    st.write("COVID-19 Total Cases by State")
    col1, col2 = st.beta_columns([2, 5])
    col1.markdown("&nbsp;")
    col2.plotly_chart(go.Figure(data=[total_cases], layout={'width': None}))

# Display Total Recovered Pie Chart
with st.beta_container():
    st.write("COVID-19 Total Recovered by State")
    col1, col2 = st.beta_columns([2, 5])
    col1.markdown("&nbsp;")
    col2.plotly_chart(go.Figure(data=[total_recovered], layout={'width': None}))

# Display Total Deaths Pie Chart
with st.beta_container():
    st.write("COVID-19 Total Deaths by State")
    col1, col2 = st.beta_columns([2, 5])
    col1.markdown("&nbsp;")
    col2.plotly_chart(go.Figure(data=[total_deaths], layout={'width': None}))

# Display Active Cases Pie Chart
with st.beta_container():
    st.write("COVID-19 Active Cases by State")
    col1, col2 = st.beta_columns([2, 5])
    col1.markdown("&nbsp;")
    col2.plotly_chart(go.Figure(data=[active], layout={'width': None}))

          
          

# Load the data from the url
url = 'https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_malaysia.csv'
cases_malaysia = pd.read_csv(url)

# Convert the date column to datetime
cases_malaysia['date'] = pd.to_datetime(cases_malaysia['date'])

# Compute the age group distribution
cases_agecat = cases_malaysia.groupby(['date']).apply(
    lambda x: pd.Series({
        'child': x.loc[x['age'] <= 11, 'cases_new'].sum(),
        'adolescent': x.loc[(x['age'] >= 12) & (x['age'] <= 17), 'cases_new'].sum(),
        'adult': x.loc[(x['age'] >= 18) & (x['age'] <= 59), 'cases_new'].sum(),
        'elderly': x.loc[x['age'] >= 60, 'cases_new'].sum()
    })
).reset_index()

# Rename the date column to 'day'
cases_agecat = cases_agecat.rename(columns={'date': 'day'})

# Convert the age group names to english
cases_agecat['cl_age90'] = cases_agecat.apply(lambda x: {
    'child': 'Children (0-11 years)',
    'adolescent': 'Adolescents (12-17 years)',
    'adult': 'Adults (18-59 years)',
    'elderly': 'Elderly (60 years and above)'
}[x.name], axis=1)

# Create a new dataframe with the totals for Malaysia
cases_malaysia_total = cases_malaysia.groupby(['date'])['cases_new'].sum().reset_index()
cases_malaysia_total = cases_malaysia_total.rename(columns={'cases_new': 'total'})

# Merge the age group distribution with the totals
cases_agecat = pd.merge(cases_agecat, cases_malaysia_total, on='day')

# Compute the percentage of cases by age group
cases_agecat['percentage'] = cases_agecat.apply(lambda x: round(100 * x[x.name] / x['total'], 2), axis=1)

# Drop the individual counts and totals columns
cases_agecat = cases_agecat.drop(['child', 'adolescent', 'adult', 'elderly', 'total'], axis=1)

# Reorder the columns
cases_agecat = cases_agecat[['day', 'cl_age90', 'percentage']]

# Show the resulting dataframe
print(cases_agecat)

          
# State Map          
url='https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv'
covid_data = pd.read_csv(url)
geojson_url = 'https://gist.githubusercontent.com/heiswayi/81a169ab39dcf749c31a/raw/b2b3685f5205aee7c35f0b543201907660fac55e/malaysia.geojson'
geojson = pd.read_json(geojson_url)

covid_data['state'] = covid_data['state'].str.title()
latest_date = str(covid_data['date'].max()).split()[0]
latest_covid_data = covid_data[covid_data['date'] == latest_date][['state', 'cases_active']].groupby(['state']).sum().reset_index()

fig1 = go.Figure(go.Choroplethmapbox(geojson=geojson, locations=latest_covid_data['state'], z=latest_covid_data['cases_active'],
                                     featureidkey='properties.name', colorscale='Blues', zmin=0, zmax=10000))

fig1.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=5, mapbox_center = {"lat": 4.195, "lon": 102.052},
                  margin=dict(l=0,r=0,b=0,t=0))

# Display map in Streamlit
st.plotly_chart(fig1)
