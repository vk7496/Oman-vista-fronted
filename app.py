import streamlit as st
import requests

# backend URL → همون Railway
BACKEND_URL = "https://fortunate-rebirth-production-93ce.up.railway.app"

st.set_page_config(page_title="OmanVista", page_icon="🌍", layout="wide")

st.title("🌍 OmanVista - AI Tourism Explorer")
st.write("Discover hidden gems of Oman with AI-powered exploration.")

# تست backend
try:
    response = requests.get(f"{BACKEND_URL}/")
    if response.status_code == 200:
        st.success("✅ Backend is connected!")
    else:
        st.error("❌ Backend not responding")
except Exception as e:
    st.error(f"Error: {e}")

# نمایش نقشه (از backend)
if st.button("Show Map"):
    try:
        map_response = requests.get(f"{BACKEND_URL}/map")
        if map_response.status_code == 200:
            st.json(map_response.json())
        else:
            st.error("Failed to fetch map data")
    except Exception as e:
        st.error(f"Error fetching map: {e}")
