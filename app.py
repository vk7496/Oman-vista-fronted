import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# ---------- Page Config ----------
st.set_page_config(
    page_title="OmanVista - AI Tourism Explorer",
    layout="wide"
)

# ---------- Background CSS ----------
def set_bg_url(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("{url}");
            background-size: cover;
            background-position: center;
        }}
        .block-container {{
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 15px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ثابت Unsplash (بک‌گراند ثابت)
set_bg_url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80")

# ---------- Multi-language ----------
lang = st.sidebar.radio("Language / اللغة", ["English", "العربية"])

texts = {
    "English": {
        "title": "OmanVista - AI Tourism Explorer 🌍",
        "desc": "Discover Oman's hidden gems - map, photos and community buzz.",
        "select": "Select a place or type custom:",
        "input": "Type a place name...",
        "images": "Number of images",
        "gallery": "📸 Photo Gallery",
        "map": "🗺 Location Map",
    },
    "العربية": {
        "title": "عُمان ڤيستا — مستكشف السياحة بالذكاء الاصطناعي 🌍",
        "desc": "اكتشف جواهر عُمان المخفية — خرائط وصور ومجتمع.",
        "select": "اختر مكانًا أو اكتب:",
        "input": "أدخل اسم المكان...",
        "images": "عدد الصور",
        "gallery": "📸 معرض الصور",
        "map": "🗺 خريطة الموقع",
    }
}

t = texts[lang]

# ---------- Sidebar ----------
st.sidebar.title(t["title"])
st.sidebar.write(t["desc"])

places = [
    "Sultan Qaboos Grand Mosque",
    "Muttrah Corniche",
    "Jebel Shams",
    "Wadi Shab",
    "Nizwa Fort"
]

place = st.sidebar.selectbox(t["select"], ["-- choose --"] + places)
custom_place = st.sidebar.text_input(t["input"])
num_images = st.sidebar.slider(t["images"], 3, 10, 5)

# ---------- Main ----------
st.title(t["title"])
st.write(t["desc"])

backend_url = "https://fortunate-rebirth-production-93ce.up.railway.app"

# Test backend
try:
    health = requests.get(f"{backend_url}/").json()
    st.success("✅ Backend is connected!")
except Exception:
    st.error("❌ Backend is not reachable.")

# Query
query = custom_place if custom_place else (place if place != "-- choose --" else None)

if query:
    st.header(f"📍 {query}")

    # ----- Map -----
    st.subheader(t["map"])
    try:
        # داده‌های نمونه برای تست نقشه
        locations = {
            "Sultan Qaboos Grand Mosque": [23.5859, 58.4078],
            "Muttrah Corniche": [23.6155, 58.5638],
            "Nizwa Fort": [22.9333, 57.5333],
            "Jebel Shams": [23.2386, 57.2742],
            "Wadi Shab": [22.8370, 59.2361],
        }

        if query in locations:
            lat, lon = locations[query]
            fmap = folium.Map(location=[lat, lon], zoom_start=10)
            folium.Marker([lat, lon], popup=query, tooltip=query).add_to(fmap)
            st_folium(fmap, width=800, height=500)
        else:
            st.info("No map data available.")
    except Exception:
        st.warning("⚠️ Map service failed.")

    # ----- Photo Gallery -----
    st.subheader(t["gallery"])
    try:
        images = requests.get(f"{backend_url}/images?query={query}&per_page={num_images}").json()
        if "results" in images:
            cols = st.columns(3)
            for idx, photo in enumerate(images["results"]):
                with cols[idx % 3]:
                    st.image(photo["url"], caption=photo.get("photographer", ""))
        else:
            st.info("No images found.")
    except Exception:
        st.warning("⚠️ Image service failed.")
