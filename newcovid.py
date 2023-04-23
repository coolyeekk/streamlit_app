import pandas as pd
import plotly.express as px
import streamlit as st

#load data
df = pd.read_csv("https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_state.csv")

#convert date strings to datetime
df['date'] = pd.to_datetime(df['date'])

#load state and district boundaries data from GeoJSON file
geojson = pd.read_json("https://raw.githubusercontent.com/jaspajjr/malaysia-geojson/main/malaysia.geojson")

#merge GeoJSON data with Covid-19 cases data
merged_df = pd.merge(df, geojson, how='left', left_on=['state', 'district'], right_on=['properties.name_1', 'properties.name_2'])

#filter data to only include selected date
selected_date = st.slider('Select a date', min_value=min(merged_df['date']), max_value=max(merged_df['date']), value=max(merged_df['date']))
filtered_df = merged_df[merged_df['date'] == selected_date]

#group cases by state and district
grouped_df = filtered_df.groupby(['properties.name_1', 'properties.name_2'])['cases_new'].sum().reset_index()

#create choropleth map with plotly
fig = px.choropleth_mapbox(grouped_df, geojson=geojson, locations=['properties.name_1', 'properties.name_2'],
                           color='cases_new', mapbox_style="carto-positron", zoom=5, center={"lat": 4.2105, "lon": 101.9758},
                           opacity=0.5, range_color=[0, max(grouped_df['cases_new'])])

#add title and colorbar legend
fig.update_layout(title_text='Covid-19 Cases by State and District in Malaysia',
                  coloraxis_colorbar=dict(title='New Cases'))

#display the plotly chart on the streamlit UI
st.plotly_chart(fig)
