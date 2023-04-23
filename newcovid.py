import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

st.markdown("<h4 style='text-align: justify; color: blue;'>This dashboard is an effort to analyze the cumulative data of Cases new,Active cases, deaths and recovered over time.</h4>", unsafe_allow_html=True)


st.markdown("<h2 style='text-align: center;'>CASES ACROSS Malaysia</h2>",
            unsafe_allow_html=True)

# kpi 1

con, rec, det, act = st.beta_columns(4)

with con:
    st.markdown("<h3 style='text-align: center;'>Cases Total</h3>",
                unsafe_allow_html=True)
    num1 = df['cases_total'][0]
    st.markdown(
        f"<h2 style='text-align: center; color: blue;'>{num1}</h2>", unsafe_allow_html=True)

with rec:
    st.markdown("<h3 style='text-align: center;'>Recovered Cases</h3>",
                unsafe_allow_html=True)
    num2 = df['recovered'][0]
    st.markdown(
        f"<h2 style='text-align: center; color: green;'>{num2}</h2>", unsafe_allow_html=True)

with det:
    st.markdown("<h3 style='text-align: center;'>Deceased Cases</h3>",
                unsafe_allow_html=True)
    num3 = df['deaths'][0]
    st.markdown(
        f"<h2 style='text-align: center; color: red;'>{num3}</h2>", unsafe_allow_html=True)

with act:
    st.markdown("<h3 style='text-align: center;'>Active Cases</h3>",
                unsafe_allow_html=True)
    num3 = df['cases_active'][0]
    st.markdown(
        f"<h2 style='text-align: center; color: orange;'>{num3}</h2>", unsafe_allow_html=True)

st.markdown("---")

# kpi2

df1 = pd.read_csv(
    "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/clusters.csv")

st.markdown("<h2 style='text-align: center;'>Visualizing Total and Daily Cases</h2>",
            unsafe_allow_html=True)

first_chart, second_chart = st.beta_columns(2)

with first_chart:
    fig = px.line(df1, x="Date", y=["Total Confirmed",
                                    "Total Deceased", "Total Recovered"], title="Total Confirmed, Recovered and Deceased")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

with second_chart:
    fig = px.line(df1, x="Date", y=["Daily Confirmed",
                                    "Daily Deceased", "Daily Recovered"], title="Daily Confirmed, Recovered and Deceased")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# kpi3

st.markdown("<h2 style='text-align: center;'>Visualizing top 5 States</h2>",
            unsafe_allow_html=True)

df2 = df[1:].sort_values('Confirmed', ascending=False)

fig = go.Figure(data=[
    go.Bar(name='Confirmed',
                x=df2['State'][:5], y=df2['Confirmed'][:5]),
    go.Bar(name='Deaths',
                x=df2['State'][:5], y=df2['Deaths'][:5]),
    go.Bar(name='Recovered',
                x=df2['State'][:5], y=df2['Recovered'][:5]), ])
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
