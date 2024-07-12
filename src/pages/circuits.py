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
        return response
    return None

##############################
# Page content
##############################

st.title("🏁 Circuits")

circuits = get_circuits()
if not circuits:
    st.error("Failed to fetch circuits.")
df = pd.DataFrame(circuits['records'])

# High level stats
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("#️⃣ Circuits", df.shape[0])
col2.metric("🗾 Countries", df['country'].nunique())
with col3:
    country_name = df['country'].mode().values[0]
    country_circuit_count = df['country'].value_counts().max()
    st.metric("🔝 Most circuits", country_name, help=f"{country_circuit_count} circuits")
with col4:
    altitude_max = df['alt'].max()
    country_name = df.loc[df['alt'].idxmax()]['country']
    st.metric("↗️ Highest Altitude", f"{altitude_max} m", help=f"{country_name}")
with col5:
    altitude_min = df['alt'].min()
    country_name = df.loc[df['alt'].idxmin()]['country']
    st.metric("↙️ Lowest Altitude", f"{altitude_min} m", help=f"{country_name}")
col6.metric("➡️ Mean Altitude", f"{round(df['alt'].mean())} m")

            
# Display the circuits on a map
map_df = df[['name', 'lat', 'lng']]
st.map(
    map_df,
    latitude='lat',
    longitude='lng',
    use_container_width=True,
    zoom=1.2,
    size=(1000)
)

# Add a table of circuits
st.write("## 💾 Circuit Data")
st.dataframe(df, use_container_width=True, hide_index=True)
