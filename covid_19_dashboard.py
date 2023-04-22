import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Load the data
data_url = "https://raw.githubusercontent.com/MoH-Malaysia/covid19-public/main/epidemic/cases_malaysia.csv"
df = pd.read_csv(data_url)

# Clean the data
df = df.dropna()
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
df["day"] = df["date"].dt.dayofyear
df["cases_per_day"] = df["cases_new"] / df["tests_new"]

# Train the model
X_train, X_test, y_train, y_test = train_test_split(df[["day"]], df["cases_per_day"], test_size=0.2, random_state=0)
model = LinearRegression()
model.fit(X_train, y_train)

# Set up the UI
st.title("Covid-19 Prediction for Malaysia")
st.write("Enter the day of the year (1-365) to get the predicted number of cases per day")

# Get user input
day = st.slider("Day of the year", 1, 365, 200)

# Make the prediction
prediction = model.predict([[day]])

# Display the prediction
st.write("Predicted number of cases per day:", prediction[0])
