import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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
df_state = pd.read_csv("https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/clusters.csv")

# Sort data by number of active cases
df2 = df_state.sort_values('cases_total', ascending=False).reset_index(drop=True)

# Create a bar chart to visualize top 5 states by active cases, deaths, and recovered cases
fig = go.Figure(data=[
    go.Bar(name='Active Cases',
                x=df2['district'][:5], y=df2['cases_total'][:5]),
    go.Bar(name='Deaths',
                x=df2['district'][:5], y=df2['deaths'][:5]),
    go.Bar(name='Recovered',
                x=df2['district'][:5], y=df2['recovered'][:5])
])

# Set title and axis labels for the chart
fig.update_layout(title='Top 5 States with Most COVID-19 Cases',
                   xaxis_title='States',
                   yaxis_title='Number of Cases')

# Display the chart in Streamlit app
st.plotly_chart(fig, use_container_width=True)


first_chart, second_chart = st.beta_columns(2)

with first_chart:
    st.markdown("<h3 style='text-align: center;'>Total Confirmed Cases</h3>",
                unsafe_allow_html=True)
    fig = px.pie(df2, values=df2["Confirmed"][:5],
                 names=df2['State'][:5])
    st.plotly_chart(fig)

with second_chart:
    st.markdown("<h3 style='text-align: center;'>Total Recovered Cases</h3>",
                unsafe_allow_html=True)
    fig = px.pie(df2, values=df2["Recovered"][:5],
                 names=df2['State'][:5])
    st.plotly_chart(fig)


first_chart, second_chart = st.beta_columns(2)

with first_chart:
    st.markdown("<h3 style='text-align: center;'>Total Active Cases</h3>",
                unsafe_allow_html=True)
    fig = px.pie(df2, values=df2["Active"][:5],
                 names=df2['State'][:5])
    st.plotly_chart(fig)

with second_chart:
    st.markdown("<h3 style='text-align: center;'>Total Deceased Cases</h3>",
                unsafe_allow_html=True)
    fig = px.pie(df2, values=df2["Deaths"][:5],
                 names=df2['State'][:5])
    st.plotly_chart(fig)

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
