from datetime import datetime
import streamlit as st
import pandas as pd
import requests

import common
common.print_menu()

##############################
# Data operations
##############################

@st.cache_data(ttl=300)
def get_circuits():
    response = requests.get(f"{st.secrets["api_url"]}/circuits?pageSize=77")
    if response.status_code == 200:
        response = response.json()
        return response['records']
    return None

@st.cache_data(ttl=300)
def get_drivers():
    response = requests.get(f"{st.secrets["api_url"]}/drivers?pageSize=900&sort=surname")
    if response.status_code == 200:
        response = response.json()
        return response['records']
    return None

##############################
# Page content
##############################

st.title("⏱️ Lap time comparator")

circuits = get_circuits()
drivers = get_drivers()
if not circuits:
    st.error("Failed to fetch circuits.")

circuit_list = [circuit["name"] for circuit in circuits]
driver_list = [f"{driver["forename"]} {driver["surname"]}" for driver in drivers]

with st.form("query_form"):
    
    qc1, qc2, qc3 = st.columns([1, 1, 0.5])
    with qc1:
        driver1 = st.selectbox("Driver", driver_list, help="Select the first driver for the compare", index=None, placeholder="Select the first driver")
    with qc2:
        driver2 = st.selectbox("Driver", driver_list, help="Select the second driver for the compare", index=None, placeholder="Select the second driver")
    with qc3:
        current_year = datetime.now().year
        year = st.text_input("Year", value="", max_chars=4, help=f"Optional: Enter a year to filter by. (Range: 1950-{current_year})", placeholder="2023")
        
    submit_button = st.form_submit_button("Compare Lap Times")

if submit_button and not driver1:
    st.error("Please select the first driver to fetch lap times for.")
    st.stop()
if submit_button and not driver2:
    st.error("Please select the second driver to fetch lap times for.")
    st.stop()
if submit_button:
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"## {driver1}")
    
        # Query data for driver 1
        driver1Id = drivers[driver_list.index(driver1)]["driverId"]
        query = ""
        if year:
            query += f"?year={year}"
        response = requests.get(f"{st.secrets["api_url"]}/races/lapTimes/{driver1Id}{query}")
        if response.status_code == 200:
            response = response.json()
            if response == []:
                st.warning(f"No lap times found for {driver1}")
            else:
                df = pd.DataFrame(response)
                df["track"] = df["circuit"].apply(lambda x: x["name"])
                df = df[['track', 'meanTime', 'fastestTime']]
                st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.error(f"Failed to fetch lap times for driver 1: {response.text}")

    with col2:
        st.write(f"## {driver2}")
    
        # Query data for driver 2
        driver2Id = drivers[driver_list.index(driver2)]["driverId"]
        query = ""
        if year:
            query += f"?year={year}"
        response = requests.get(f"{st.secrets["api_url"]}/races/lapTimes/{driver2Id}{query}")
        if response.status_code == 200:
            response = response.json()
            if response == []:
                st.warning(f"No lap times found for driver 1: {driver1}")
            else:
                df = pd.DataFrame(response)
                df["track"] = df["circuit"].apply(lambda x: x["name"])
                df = df[['track', 'meanTime', 'fastestTime']]
                st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.error(f"Failed to fetch lap times for driver 2: {response.text}")
