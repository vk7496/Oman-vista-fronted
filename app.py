import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# ===============================
# BACKGROUND IMAGE
# ===============================
def set_background():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(page_title="OmanVista", layout="wide")

st.title("🌍 OmanVista - AI Tourism Explorer")
st.markdown("Discover hidden gems of Oman with AI-powered exploration.")

# ===============================
# BACKEND CONNECTION
# ===============================
BACKEND_URL = "https://fortunate-rebirth-production-93ce.up.railway.app"

try:
    r = requests.get(f"{BACKEND_URL}/")
    if r.status_code == 200:
        st.success("✅ Backend is connected!")
    else:
        st.error("❌ Backend not reachable")
except Exception as e:
    st.error(f"⚠️ Connection error: {e}")

# ===============================
# MAP SECTION
# ===============================
st.subheader("🗺️ Map")

def show_map(lat, lon, zoom=13):
    m = folium.Map(location=[lat, lon], zoom_start=zoom)
    folium.Marker([lat, lon], popup="Selected Location 📍").add_to(m)
    st_folium(m, width=700, height=500)

if st.button("Show Map"):
    show_map(23.5859, 58.4078)  # مسجد سلطان قابوس

# ===============================
# PHOTO GALLERY
# ===============================
st.subheader("📸 Photo Gallery")

def get_unsplash_images(query, count=6):
    return [
        f"https://source.unsplash.com/800x600/?{query.replace(' ', ',')}&sig={i}"
        for i in range(count)
    ]

if st.button("Show Images"):
    images = get_unsplash_images("Oman tourism", 6)
    cols = st.columns(3)
    for i, img_url in enumerate(images):
        with cols[i % 3]:
            st.image(img_url, use_container_width=True)

# ===============================
# QUICK INFO
# ===============================
st.subheader("🔎 Quick Info")
st.write("**Place:** Sultan Qaboos Grand Mosque")
st.write("**Coordinates:** 23.5859, 58.4078")
st.write("**Region:** Muscat")

# ===============================
# COMMUNITY BUZZ
# ===============================
st.subheader("📢 Community Buzz")
st.write("Reddit / Twitter API integration coming soon 🚀")
