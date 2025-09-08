import streamlit as st
import requests
import base64

# 🌍 پشتیبانی دو زبانه
LANG = {
    "en": {
        "title": "OmanVista — AI Tourism Explorer 🌍",
        "subtitle": "Discover Oman's hidden gems — map, photos and community buzz.",
        "sidebar_title": "OmanVista — AI Tourism Explorer 🌍",
        "sidebar_desc": "Discover Oman’s hidden gems — map, photos and community buzz.",
        "select_place": "Select place or type custom:",
        "type_place": "Type a place name...",
        "num_images": "Number of images",
        "map": "Map",
        "photos": "Photos",
        "buzz": "Community Buzz",
        "backend_error": "⚠️ Could not fetch data from backend.",
        "no_data": "No data available."
    },
    "ar": {
        "title": "OmanVista — مستكشف السياحة بالذكاء الاصطناعي 🌍",
        "subtitle": "اكتشف جواهر عُمان الخفية — خريطة، صور ومجتمع.",
        "sidebar_title": "OmanVista — مستكشف السياحة 🌍",
        "sidebar_desc": "اكتشف جواهر عُمان الخفية — خريطة، صور ومجتمع.",
        "select_place": "اختر مكانًا أو اكتب:",
        "type_place": "اكتب اسم المكان...",
        "num_images": "عدد الصور",
        "map": "الخريطة",
        "photos": "الصور",
        "buzz": "آراء المجتمع",
        "backend_error": "⚠️ لم نتمكن من جلب البيانات من الخادم.",
        "no_data": "لا توجد بيانات متاحة."
    }
}

# 🎨 CSS برای پس‌زمینه
def set_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{"png"};base64,{encoded});
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# 📌 بک‌گراند (یک عکس sunset در پوشه پروژه بگذار)
set_bg("sunset.jpg")

# 🌐 انتخاب زبان
lang_choice = st.sidebar.radio("Language / اللغة", ["en", "ar"])
lang_text = LANG[lang_choice]

# 📝 Sidebar
st.sidebar.title(lang_text["sidebar_title"])
st.sidebar.info(lang_text["sidebar_desc"])

places = ["Muscat", "Nizwa", "Salalah", "Sur", "Muttrah Souq", "Jebel Akhdar"]

selected_place = st.sidebar.selectbox(lang_text["select_place"], ["-- choose --"] + places)
custom_place = st.sidebar.text_input(lang_text["type_place"])
num_images = st.sidebar.slider(lang_text["num_images"], 1, 10, 5)

# 🏷️ Title
st.title(lang_text["title"])
st.write(lang_text["subtitle"])

# 📡 Backend URL
BACKEND_URL = "https://fortunate-rebirth-production-93ce.up.railway.app"

# ✅ اگر مکانی انتخاب شده
place = custom_place if custom_place else (selected_place if selected_place != "-- choose --" else None)

if place:
    try:
        response = requests.get(f"{BACKEND_URL}/explore", params={"place": place, "num_images": num_images})
        if response.status_code == 200:
            data = response.json()

            # 🗺️ نقشه
            st.subheader("🗺️ " + lang_text["map"])
            st.components.v1.html(data.get("map", ""), height=500)

            # 📸 تصاویر
            st.subheader("📸 " + lang_text["photos"])
            images = data.get("images", [])
            if images:
                for img in images:
                    st.image(img["url"], caption=img["photographer"])
            else:
                st.info(lang_text["no_data"])

            # 💬 Buzz
            st.subheader("💬 " + lang_text["buzz"])
            buzz_posts = data.get("buzz", [])
            if buzz_posts:
                for post in buzz_posts:
                    st.write(f"**{post.get('title','')}** — {post.get('source','')}")
            else:
                st.info(lang_text["no_data"])

        else:
            st.error(lang_text["backend_error"])
    except Exception as e:
        st.error(f"{lang_text['backend_error']} ({str(e)})")
