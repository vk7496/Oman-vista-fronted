import streamlit as st
import requests

# ===== Language Texts =====
LANG_TEXTS = {
    "en": {
        "title": "OmanVista: AI Tourism Explorer 🌍",
        "map": "Map",
        "photo_gallery": "Photo Gallery",
        "quick_info": "Quick info",
        "community_buzz": "Community Buzz",
        "no_photos": "No photos available.",
        "no_posts": "No community posts available."
    },
    "ar": {
        "title": "عُمان ڤيستا: مستكشف السياحة بالذكاء الاصطناعي 🌍",
        "map": "الخريطة",
        "photo_gallery": "معرض الصور",
        "quick_info": "معلومات سريعة",
        "community_buzz": "آراء المجتمع",
        "no_photos": "لا توجد صور متاحة.",
        "no_posts": "لا توجد منشورات مجتمعية متاحة."
    }
}

# ===== Sidebar language switch =====
lang = st.sidebar.radio("Language / اللغة", ["en", "ar"])
T = LANG_TEXTS[lang]

st.set_page_config(page_title="OmanVista", layout="wide")

# ===== Background CSS =====
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://source.unsplash.com/1600x900/?oman,landscape");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ===== Title =====
st.title(T["title"])

# ===== Map Section =====
st.subheader(T["map"])
st.map({"lat": [23.5880], "lon": [58.3829]})  # Muscat example

# ===== Photo Gallery Section =====
st.subheader(T["photo_gallery"])
try:
    resp = requests.get("https://fortunate-rebirth-production-93ce.up.railway.app/images?query=Oman")
    if resp.status_code == 200:
        data = resp.json()
        if data["results"]:
            for img in data["results"]:
                st.image(img["url"], caption=img["photographer"], use_container_width=True)
        else:
            st.info(T["no_photos"])
    else:
        st.info(T["no_photos"])
except Exception:
    st.info(T["no_photos"])

# ===== Reddit / Community Buzz Section =====
st.subheader(T["community_buzz"])
try:
    resp = requests.get("https://www.reddit.com/r/travel/top.json?limit=3", headers={"User-agent": "OmanVistaBot"})
    if resp.status_code == 200:
        posts = resp.json()["data"]["children"]
        if posts:
            for p in posts:
                st.write(f"**{p['data']['title']}**")
        else:
            st.info(T["no_posts"])
    else:
        st.info(T["no_posts"])
except Exception:
    st.info(T["no_posts"])
