from datetime import datetime
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

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

# Convert milliseconds to "minutes:seconds.milliseconds"
def format_time(milliseconds):
    minutes = milliseconds // 60000
    seconds = (milliseconds % 60000) // 1000
    millis = milliseconds % 1000
    return f"{int(minutes)}:{int(seconds):02d}.{int(millis):03d}"

##############################
# Page content
##############################

st.title("⏱️ Driver Lap Performance")

circuits = get_circuits()
drivers = get_drivers()
if not circuits:
    st.error("Failed to fetch circuits.")

circuit_list = [circuit["name"] for circuit in circuits]
driver_list = [f"{driver["forename"]} {driver["surname"]}" for driver in drivers]

with st.form("query_form"):
    qc1, qc2, qc3 = st.columns([1, 1.5, 0.5])
    with qc1:
        driver = st.selectbox("Driver", driver_list, help="Select a driver to filter laptimes for", index=None, placeholder="Select a driver")
    with qc2:
        circuit = st.selectbox("Circuit", circuit_list, help="Select a circuit to fetch lap times for.", index=None, placeholder="Select a circuit")
    with qc3:
        current_year = datetime.now().year
        year = st.text_input("Year", value="", max_chars=4, help=f"Optional: Enter a year to filter by. (Range: 1950-{current_year})", placeholder="2023")
    submit_button = st.form_submit_button("Fetch Lap Times")

if submit_button and not driver:
    st.error("Please select a driver to fetch lap times for.")
    st.stop()
if submit_button and not circuit:
    st.error("Please select a circuit to fetch lap times for.")
    st.stop()

if submit_button and driver:
    selected_driver = drivers[driver_list.index(driver)]
    query = f"pageSize=1000&filter=driverId={selected_driver["driverId"]}"
    if circuit:
        query += f",race.circuit.name={circuit}"
    if year:
        query += f",race.year={year}"
    query_url = f"{st.secrets['api_url']}/races/lapTimes?{query}"

    response = requests.get(query_url)
    if response.status_code == 200:       
        data = response.json()["records"]

        if data == []:
            st.error("No data available for the selected filters.")
            st.stop()

        # Convert the data to a DataFrame and display it
        df = pd.DataFrame(data)
        if not circuit:
            df["circuit"] = df["race"].apply(lambda x: x["circuit"]["name"])
            df = df[["circuit", "lap", "position", "time", "milliseconds"]]
        else:
            col1, col2, col3 = st.columns([1, 1, 1])
            col1.metric("#️⃣ No. of laps tracked", df["lap"].nunique())
            fastest_lap = df["time"].min()
            fastest_lap_record = df[df["time"] == fastest_lap].iloc[0]
            col2.metric("⏱️ Fastest Lap", df["time"].min(), help=f"Year: {fastest_lap_record["race"]["year"]}")

            # Mean lap time
            df["time_td"] = pd.to_timedelta(df["time"].apply(lambda x: "0:" + x if len(x.split(':')) == 2 else x))
            mean_lap_time_td = df["time_td"].mean()
            total_seconds = mean_lap_time_td.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = total_seconds % 60
            formatted_mean_lap_time = f"{minutes}:{seconds:06.3f}"
            col3.metric("➡️ Average Lap Time", formatted_mean_lap_time)

            # Graph of time plotted against lap number
            df['formatted_time'] = df['milliseconds'].apply(format_time)
            df['race_year'] = df["race"].apply(lambda x: x["year"])
            df['race_round'] = df["race"].apply(lambda x: x["round"])
            if not year:
                fig = px.scatter(
                    df, 
                    x="lap",
                    y="milliseconds", 
                    labels={"lap": "Lap Number", "milliseconds": "Time"},
                    text="formatted_time",
                    color="race_year",
                )
            else:
                fig = px.scatter(
                    df, 
                    x="lap", 
                    y="milliseconds", 
                    labels={"lap": "Lap Number", "milliseconds": "Time"},
                    text="formatted_time",
                )
            fig.update_traces(mode="markers")
            chart_step = 5000
            fig.update_yaxes(tickmode='array',
                 tickvals=[i * chart_step for i in range((df['milliseconds'].max() // chart_step) + 1)], 
                 ticktext=[format_time(i * chart_step) for i in range((df['milliseconds'].max() // chart_step) + 1)])
            st.plotly_chart(fig, use_container_width=True)

            df = df[["lap", "position", "time", "milliseconds"]]
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.error(f"Failed to fetch data. Please try again. {response.text}")