import streamlit as st
import requests
import base64
import folium
from streamlit_folium import st_folium

# ---------- Background ----------
def set_bg(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_bg("sunset.jpg")  # مطمئن شو sunset.jpg داخل فولدر frontend هست

# ---------- Multilingual ----------
LANG = st.sidebar.radio("🌐 Language / اللغة", ["English", "العربية"])

texts = {
    "English": {
        "title": "🏝️ OmanVista: AI Tourism Explorer",
        "desc": "Discover Oman’s hidden gems — maps, photos, and community buzz.",
        "place": "Select a place",
        "map": "🗺️ Map",
        "photos": "📸 Photos",
        "reddit": "💬 Reddit Community",
    },
    "العربية": {
        "title": "🏝️ عمان فيستا: مستكشف السياحة بالذكاء الاصطناعي",
        "desc": "اكتشف كنوز عمان الخفية — خرائط، صور، ونبض المجتمع.",
        "place": "اختر مكاناً",
        "map": "🗺️ الخريطة",
        "photos": "📸 الصور",
        "reddit": "💬 مجتمع ريديت",
    },
}

t = texts[LANG]

# ---------- Backend URL ----------
backend_url = "https://fortunate-rebirth-production-93ce.up.railway.app"

# ---------- Sidebar ----------
st.sidebar.title("⚙️ Options")
place = st.sidebar.text_input(t["place"], "Muscat")

# ---------- Main Title ----------
st.title(t["title"])
st.markdown(f"**{t['desc']}**")

# ---------- Map ----------
st.subheader(t["map"])
try:
    map_data = requests.get(f"{backend_url}/map?query={place}").json()
    if "lat" in map_data and "lon" in map_data:
        lat, lon = float(map_data["lat"]), float(map_data["lon"])
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], tooltip=place).add_to(m)
        st_folium(m, width=700, height=500)
    else:
        st.warning("⚠️ No coordinates found.")
except Exception:
    st.warning("⚠️ Map service failed.")

# ---------- Photos ----------
st.subheader(t["photos"])
try:
    images = requests.get(f"{backend_url}/images?query={place}&per_page=6").json()
    if "results" in images:
        cols = st.columns(3)
        for i, photo in enumerate(images["results"]):
            with cols[i % 3]:
                st.image(photo["url"], caption=photo["photographer"])
    else:
        st.warning("⚠️ No images available.")
except Exception:
    st.warning("⚠️ Photo service failed.")

# ---------- Reddit ----------
st.subheader(t["reddit"])
try:
    reddit = requests.get(f"{backend_url}/reddit?query={place}").json()
    if "posts" in reddit and reddit["posts"]:
        for post in reddit["posts"]:
            st.markdown(f"🔗 [{post['title']}]({post['url']})")
    else:
        st.info("No Reddit posts found.")
except Exception:
    st.warning("⚠️ Reddit service failed.")
