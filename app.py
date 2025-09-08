import streamlit as st
import requests

# ---------- تنظیمات صفحه ----------
st.set_page_config(
    page_title="OmanVista – AI Tourism Explorer",
    layout="wide"
)

# ---------- CSS بک‌گراند ----------
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
            background: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# بک‌گراند اینترنتی (unsplash)
set_bg_url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1600&q=80")

# ---------- زبان ----------
lang = st.sidebar.radio("Language / اللغة", ["en", "ar"])

texts = {
    "en": {
        "title": "OmanVista — AI Tourism Explorer 🌍",
        "desc": "Discover Oman’s hidden gems — map, photos and community buzz.",
        "select": "Select place or type custom:",
        "input": "Type a place name...",
        "images": "Number of images"
    },
    "ar": {
        "title": "عُمان ڤيستا — مستكشف السياحة بالذكاء الاصطناعي 🌍",
        "desc": "اكتشف جواهر عُمان المخفية — خرائط، صور، ومجتمع.",
        "select": "اختر مكانًا أو اكتب:",
        "input": "أدخل اسم المكان...",
        "images": "عدد الصور"
    }
}

t = texts[lang]

# ---------- نوار کناری ----------
st.sidebar.title(t["title"])
st.sidebar.write(t["desc"])

places = ["Sultan Qaboos Grand Mosque", "Muttrah Corniche", "Jebel Shams", "Wadi Shab", "Nizwa Fort"]

place = st.sidebar.selectbox(t["select"], ["-- choose --"] + places)
custom_place = st.sidebar.text_input(t["input"])
num_images = st.sidebar.slider(t["images"], 3, 10, 5)

# ---------- بخش اصلی ----------
st.title(t["title"])
st.write(t["desc"])

# اتصال به backend
backend_url = "https://fortunate-rebirth-production-93ce.up.railway.app"

try:
    health = requests.get(f"{backend_url}/").json()
    st.success("✅ Backend is connected!")
except Exception:
    st.error("❌ Backend is not reachable.")

# اگر مکانی انتخاب یا وارد شد
query = custom_place if custom_place else (place if place != "-- choose --" else None)

if query:
    st.header(f"📍 {query}")

    # 🗺 نقشه
    try:
        map_data = requests.get(f"{backend_url}/map?query={query}").json()
        if "lat" in map_data and "lon" in map_data:
            st.map([{"lat": map_data["lat"], "lon": map_data["lon"]}])
    except Exception as e:
        st.warning("Map service failed.")

    # 🖼 گالری تصاویر
    st.subheader("📸 Photo Gallery")
    try:
        images = requests.get(f"{backend_url}/images?query={query}&per_page={num_images}").json()
        if "results" in images:
            cols = st.columns(3)
            for idx, photo in enumerate(images["results"]):
                with cols[idx % 3]:
                    st.image(photo["url"], caption=photo.get("photographer", ""))
    except Exception as e:
        st.warning("Image service failed.")

    # 📰 Reddit (Community Buzz)
    st.subheader("📰 Community Buzz (Reddit)")
    try:
        reddit = requests.get(f"{backend_url}/reddit?query={query}").json()
        if "posts" in reddit:
            for post in reddit["posts"]:
                st.markdown(f"🔗 [{post['title']}]({post['url']})")
        else:
            st.info("No Reddit posts found.")
    except Exception:
        st.warning("Reddit service failed.")
