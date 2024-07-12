import streamlit as st
import pandas as pd
import requests

from datetime import datetime

import common
common.print_menu()

##############################
# Data operations
##############################

@st.cache_data(ttl=300)
def get_next_race():
    # Get todays date in the format YYYY-MM-DD
    today = datetime.today().strftime('%Y-%m-%d')
    response = requests.get(f"{st.secrets["api_url"]}/races?pageSize=1&filter=date%3E{today}&sort=date&order=asc")
    if response.status_code == 200:
        response = response.json()
        return response["records"][0]
    return None

##############################
# Page content
##############################

st.title("🏎️ Races")

# Next Grand Prix information
next_race = get_next_race()
if not next_race:
    st.error("Failed to fetch Race data.")

st.metric("⏭️ Next Race", next_race["name"])
col1, col2, col3, col4, col5 = st.columns([0.5, 1, 0.75, 1, 1])
col1.metric("#️⃣ Round", next_race["round"])
col2.metric("📅 Date", next_race["date"].split("T")[0])
col3.metric("⏰ Time", next_race["time"])
col4.metric("🌍 Location", next_race["circuit"]["location"])
col5.metric("🏟️ Circuit", next_race["circuit"]["name"])
st.divider()

# Self service query section with updating dataframe
st.header("💾 Custom Query")

with st.form("query_form"):
    qc1, qc2, qc3, qc4 = st.columns([0.5, 0.75, 1, 0.5])
    with qc1:
        page = st.number_input("Page", min_value=1, value=1, help="Page number to fetch")
    with qc2:
        pageSize = st.number_input("Page Size", min_value=1, max_value=1000, value=10, help="Number of records per page (range: 1-1000)")
    with qc3:
        sort = st.selectbox("Sort by column", ["", "raceId", "year", "round", "circuitId", "name", "date", "time"], help="Column to sort by")
    with qc4:
        order = st.selectbox("Order", ["asc", "desc"], help="Sort order")
    
    custom_filter_query = st.text_input("Custom filter query", help="Enter multiple custom LINQ supported query, comma-separated (eg: `year=2023,circuit.location=Silverstone`)")
    keep_columns = st.text_input("Columns to keep", help="Enter column names to keep, comma-separated (eg: `raceId,year,round`)")
    submit_button = st.form_submit_button("Submit Query")

if submit_button:
    # Construct the query URL
    query_url = f"{st.secrets['api_url']}/races?page={page}&pageSize={pageSize}"
    if custom_filter_query:
        query_url += f"&filter={custom_filter_query}"
    if sort:
        query_url += f"&sort={sort}"
    if order:
        query_url += f"&order={order}"
    
    # Fetch data from the API
    response = requests.get(query_url)
    if response.status_code == 200:
        metadata = response.json()["_metadata"]
        # Collapsible section to display metadata as json
        with st.expander("ℹ️ Metadata", expanded=False):
            st.json(metadata)
        
        data = response.json()["records"]
        # Convert the data to a DataFrame and display it
        df = pd.DataFrame(data)
        if keep_columns:
            keep_columns = keep_columns.split(",")
            df = df[keep_columns]
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.error(f"Failed to fetch data. Please try again. {response.text}")