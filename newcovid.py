import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from plotly.subplots import make_subplots

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
st.plotly_chart(fig, use_container_width=True)



# Pie Chart
# Read data from MoH Malaysia dataset
df_clusters = pd.read_csv("https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/clusters.csv")

# Group data by state and calculate the sum of cases, recoveries, deaths, and new cases
state_grouped = df_clusters.groupby('district').agg({'cases_total': 'sum', 'recovered': 'sum', 'deaths': 'sum', 'cases_new': 'sum'}).reset_index()
state_grouped = state_grouped.sort_values('cases_total', ascending=False).head(5)

# Create pie chart data for each case type
total_cases = go.Pie(labels=state_grouped['district'], values=state_grouped['cases_total'], name='Total Cases')
total_recovered = go.Pie(labels=state_grouped['district'], values=state_grouped['recovered'], name='Total Recovered')
total_deaths = go.Pie(labels=state_grouped['district'], values=state_grouped['deaths'], name='Total Deaths')
new_cases = go.Pie(labels=state_grouped['district'], values=state_grouped['cases_new'], name='New Cases')

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

# Display New Cases Pie Chart
with st.beta_container():
    st.write("COVID-19 New Cases by State")
    col1, col2 = st.beta_columns([2, 5])
    col1.markdown("&nbsp;")
    col2.plotly_chart(go.Figure(data=[new_cases], layout={'width': None}))


# Scattermap
lat_lon = pd.read_csv("lat_lon_india.csv")
df.drop(0, axis=0, inplace=True)
df.reset_index(drop=True, inplace=True)
df["lat"] = lat_lon['latitude']
df["lon"] = lat_lon['longitude']

fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name="State", hover_data=["Confirmed", "Recovered", "Deaths", "Active"],
                        color_discrete_sequence=["darkblue"], zoom=4, height=700)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.markdown("<h2 style='text-align: center;'>State-wise detailed Scattermap</h2>",
            unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
