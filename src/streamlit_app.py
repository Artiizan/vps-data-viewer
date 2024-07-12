import streamlit as st
import requests

import common
common.print_menu()

def get_metrics():
    response = requests.get(f"{st.secrets["api_url"]}/database/metrics")
    if response.status_code == 200:
        return response.json()
    return None

st.markdown("""
    # 🚗 Vehicle Performance Software - Data Viewer
    This Streamlit powered dashboard contains a comprehensive Data Insights Platform designed to allow users to parse, manipulate, and visualize data.<br>
    The platform is divided into three main components: a dataset parser, REST API, and a Streamlit dashboard.

    ### ❓ Why Streamlit?
    Streamlit was chosen as a platform to visualise the data due to its rapid prototyping capabilities and ease of use.
    Given the time constraints of the challenge, Streamlit allowed for quick iteration and deployment, while still providing a deep level of data visualisation and interactivity.

    ### 💽 Repository Links
    For more details, visit my GitHub repositories:
        
    - [vps-rest-api](https://github.com/Artiizan/vps-rest-api)
    - [vps-data-viewer](https://github.com/Artiizan/vps-data-viewer)

    ### 📈 Database Table Counts
""", unsafe_allow_html=True)

# Fetch and display database metrics
metrics = get_metrics()
if metrics:
    columns = st.columns([2, *([3] * len(metrics)), 2]) # Add outer columns for padding
    for col, (table_name, count) in zip(columns[1:-1], metrics.items()):
        formatted_count = f"{count:,}"
        label_parts = table_name.split("_")
        formatted_label = " ".join([part.capitalize() for part in label_parts])
        col.metric(label=formatted_label, value=formatted_count)
else:
    st.error("Failed to fetch database metrics.")
