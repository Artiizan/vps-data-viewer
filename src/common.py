import os
import logging
import streamlit as st
from pathlib import Path

logo_path = os.path.join(os.path.abspath(os.getcwd()), "src/resources", "logo.png")

def print_menu():
    st.set_page_config(
        page_title="VPS - Data Viewer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    """
    Prints the logo at the top of the Streamlit sidebar.
    """

    pil_logger = logging.getLogger("PIL")
    pil_logger.setLevel(logging.INFO)

    # draw the app header
    if os.path.exists(logo_path):
        col_icon, col_title = st.sidebar.columns([1.3, 2])
        image = Path(logo_path).read_bytes()
        col_icon.markdown("<br>", unsafe_allow_html=True)
        col_icon.image(image, use_column_width=True)
        col_title.header('Vehicle Performance Software')
    else:
        col_title, _ = st.sidebar.columns([2, 0.8])
        st.sidebar.header('Vehicle Performance Software')

    # draw available pages
    with st.sidebar:
        st.page_link("streamlit_app.py", label="Home", icon="🏠")
        st.write("")
        st.header("Tracks")
        st.page_link("pages/circuits.py", label="Circuits", icon="🏁")
        st.page_link("pages/races.py", label="Race Events", icon="🏎️")
        st.page_link("pages/lap_times.py", label="Lap Time Comparator", icon="🕒")
        st.header("Drivers")
        st.page_link("pages/drivers.py", label="Drivers", icon="👨‍🚀")
        st.page_link("pages/driver_performance.py", label="Driver Performance", icon="🕒")
