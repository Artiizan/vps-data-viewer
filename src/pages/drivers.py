import streamlit as st
import pandas as pd
import requests

import common
common.print_menu()

##############################
# Data operations
##############################

@st.cache_data(ttl=300)
def driver_with_most_points():
    response = requests.get(f"{st.secrets["api_url"]}/drivers/standings?pageSize=1&sort=points&order=dsc")
    if response.status_code == 200:
        response = response.json()
        return response["records"][0]
    return None

@st.cache_data(ttl=300)
def driver_with_most_wins():
    response = requests.get(f"{st.secrets["api_url"]}/drivers/standings?pageSize=1&sort=wins&order=dsc")
    if response.status_code == 200:
        response = response.json()
        return response["records"][0]
    return None

##############################
# Page content
##############################

st.title("👨‍🚀 Drivers")

# All time driver stats
most_points = driver_with_most_points()
most_wins = driver_with_most_wins()
if not most_points or not most_wins:
    st.error("Failed to fetch driver standings.")

col1, col2 = st.columns([1, 1])
most_points_driver_name = f"{most_points["driver"]["forename"]} {most_points["driver"]["surname"]}"
col1.metric("🏆 Most Points in a season", most_points_driver_name, most_points["points"], help=f"Achieved in {most_points["race"]["year"]}")
most_wins_driver_name = f"{most_wins["driver"]["forename"]} {most_wins["driver"]["surname"]}"
col2.metric("🏁 Most Wins in a season", most_wins_driver_name, most_wins["wins"], help=f"Achieved in {most_wins["race"]["year"]}")

# Self service query section with updating dataframe
st.header("💾 Custom Query")

with st.form("query_form"):
    qc1, qc2, qc3, qc4 = st.columns([0.5, 0.75, 1, 0.5])
    with qc1:
        page = st.number_input("Page", min_value=1, value=1, help="Page number to fetch")
    with qc2:
        pageSize = st.number_input("Page Size", min_value=1, max_value=1000, value=10, help="Number of records per page (range: 1-1000)")
    with qc3:
        sort = st.selectbox("Sort by column", ["", "raceId", "driverId", "points", "position", "wins"], help="Column to sort by")
    with qc4:
        order = st.selectbox("Order", ["asc", "desc"], help="Sort order")
    
    custom_filter_query = st.text_input("Custom filter query", help="Enter multiple custom LINQ supported query, comma-separated (eg: `race.year=2023,driver.code=ALB`)")
    keep_columns = st.text_input("Columns to keep", help="Enter column names to keep, comma-separated (eg: `race,driver,points,wins`)")
    submit_button = st.form_submit_button("Submit Query")

if submit_button:
    # Construct the query URL
    query_url = f"{st.secrets['api_url']}/drivers/standings?page={page}&pageSize={pageSize}"
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