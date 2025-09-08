# frontend/app.py
import os
import streamlit as st
import requests
import folium
import streamlit.components.v1 as components
from io import BytesIO
from urllib.parse import quote_plus
from PIL import Image

# ---------------- page config ----------------
st.set_page_config(page_title="OmanVista", page_icon="🌍", layout="wide")

# ---------------- background CSS ----------------
BG_URL = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"  # قابل تغییر به عکس عمان
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{BG_URL}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    .stSidebar .sidebar-content {{
        background: rgba(255,255,255,0.92);
    }}
    .main .block-container {{
        background: rgba(255,255,255,0.92);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- backend config ----------------
# Set this in Streamlit Secrets: {"BACKEND_URL": "https://fortunate-rebirth-production-93ce.up.railway.app"}
BACKEND_URL = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "https://fortunate-rebirth-production-93ce.up.railway.app"))

# ---------------- translation texts ----------------
TXT = {
    "en": {
        "title": "OmanVista — AI Tourism Explorer 🌍",
        "subtitle": "Discover Oman’s hidden gems — map, photos and community buzz.",
        "select_place": "Select place or type custom:",
        "place_custom": "Type a place name...",
        "img_count": "Number of images",
        "show_map": "Show Map",
        "show_images": "Show Images",
        "fetch_reddit": "Fetch Reddit Posts",
        "backend_connected": "✅ Backend connected",
        "backend_failed": "❌ Backend not reachable",
        "no_photos": "No photos available.",
        "no_posts": "No community posts available.",
        "quick_info": "Quick info",
        "coords": "Coordinates",
        "region": "Region",
    },
    "ar": {
        "title": "عُمان فيستا — مستكشف السياحة بالذكاء الاصطناعي 🌍",
        "subtitle": "اكتشف جواهر عُمان المخفية — خريطة، صور وحديث المجتمع.",
        "select_place": "اختر مكاناً أو اكتب مخصص:",
        "place_custom": "اكتب اسم المكان...",
        "img_count": "عدد الصور",
        "show_map": "عرض الخريطة",
        "show_images": "عرض الصور",
        "fetch_reddit": "جلب منشورات Reddit",
        "backend_connected": "✅ الاتصال بالبك‌اند متصل",
        "backend_failed": "❌ لا يوجد اتصال بالبك‌اند",
        "no_photos": "لا توجد صور متاحة.",
        "no_posts": "لا توجد منشورات مجتمعية.",
        "quick_info": "معلومات سريعة",
        "coords": "الإحداثيات",
        "region": "المنطقة",
    }
}

# ---------------- attractions (static) ----------------
ATTRACTIONS = [
    {"id":"sultan_qaboos","name_en":"Sultan Qaboos Grand Mosque","name_ar":"جامع السلطان قابوس","lat":23.5859,"lon":58.4078,"region":"Muscat"},
    {"id":"mutrah","name_en":"Mutrah Corniche","name_ar":"كورنيش مطرح","lat":23.6155,"lon":58.5638,"region":"Muscat"},
    {"id":"nizwa","name_en":"Nizwa Fort","name_ar":"قلعة نزوى","lat":22.9333,"lon":57.5333,"region":"Ad Dakhiliyah"},
    {"id":"jebel_shams","name_en":"Jebel Shams","name_ar":"جبل شمس","lat":23.2386,"lon":57.2742,"region":"Ad Dakhiliyah"},
    {"id":"wadi_shab","name_en":"Wadi Shab","name_ar":"وادي شاب","lat":22.8861,"lon":59.0136,"region":"Ash Sharqiyah"},
]

# ---------------- sidebar controls ----------------
lang = st.sidebar.radio("Language / اللغة", ["en", "ar"], index=0)
L = TXT[lang]

st.sidebar.title(L["title"])
st.sidebar.write(L["subtitle"])

place_options = [p["name_en"] if lang=="en" else p["name_ar"] for p in ATTRACTIONS]
sel_index = st.sidebar.selectbox(L["select_place"], options=["-- choose --"] + place_options)
custom_place = st.sidebar.text_input(L["place_custom"], "")
img_count = st.sidebar.slider(L["img_count"], min_value=3, max_value=12, value=6, step=1)

# determine selected place
if custom_place.strip():
    sel_name = custom_place.strip()
    sel_lat, sel_lon, sel_region = None, None, ""
else:
    if sel_index != "-- choose --":
        # find attraction dict
        idx = place_options.index(sel_index)
        sel_item = ATTRACTIONS[idx]
        sel_name = sel_item["name_en"] if lang=="en" else sel_item["name_ar"]
        sel_lat = sel_item["lat"]
        sel_lon = sel_item["lon"]
        sel_region = sel_item.get("region","")
    else:
        # default Muscat
        sel_item = ATTRACTIONS[0]
        sel_name = sel_item["name_en"] if lang=="en" else sel_item["name_ar"]
        sel_lat = sel_item["lat"]
        sel_lon = sel_item["lon"]
        sel_region = sel_item.get("region","")

# ---------------- header ----------------
st.title(L["title"])
st.write(L["subtitle"])
st.write("---")

# ---------------- backend status ----------------
try:
    r = requests.get(f"{BACKEND_URL}/", timeout=4)
    if r.ok:
        st.success(L["backend_connected"])
    else:
        st.warning(L["backend_failed"])
except Exception:
    st.error(L["backend_failed"])

# ---------------- helper functions ----------------
@st.cache_data(ttl=300)
def fetch_image_bytes(url: str):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.content
    except Exception:
        return None

@st.cache_data(ttl=180)
def fetch_images_from_backend(query: str, per: int = 6):
    try:
        r = requests.get(f"{BACKEND_URL}/images", params={"q": query, "per": per}, timeout=8)
        if r.ok:
            data = r.json()
            # normalize: return list of url strings
            urls = []
            # common keys
            for key in ("images","results","photos"):
                v = data.get(key)
                if isinstance(v, list):
                    for it in v:
                        if isinstance(it, str):
                            urls.append(it)
                        elif isinstance(it, dict):
                            # try many fields
                            for k in ("url","src","image","regular","large","medium","original"):
                                val = it.get(k)
                                if isinstance(val, str):
                                    urls.append(val); break
                                if isinstance(val, dict):
                                    for kk in ("large","medium","original","regular"):
                                        if val.get(kk):
                                            urls.append(val.get(kk)); break
            # top-level list fallback
            if not urls and isinstance(data, list):
                for it in data:
                    if isinstance(it, str):
                        urls.append(it)
            return urls[:per]
    except Exception:
        return []
    return []

def unsplash_fallback(query: str, per: int = 6):
    return [f"https://source.unsplash.com/1200x800/?{quote_plus(query)},oman&sig={i}" for i in range(per)]

# ---------------- layout: two columns ----------------
col_left, col_right = st.columns([2,1])

# ---- left: map + gallery ----
with col_left:
    st.subheader("🗺️ " + L["map"])
    if st.button(L["show_map"]):
        # build map
        m = folium.Map(location=[sel_lat or 23.5880, sel_lon or 58.3829], zoom_start=11)
        for a in ATTRACTIONS:
            popup = a["name_en"] if lang=="en" else a["name_ar"]
            folium.Marker([a["lat"], a["lon"]], popup=popup).add_to(m)
        if sel_lat and sel_lon:
            folium.CircleMarker([sel_lat, sel_lon], radius=8, color="#ff5722", fill=True, fill_color="#ff5722").add_to(m)
        # render as HTML to keep persistent
        html = m.get_root().render()
        components.html(html, height=560)

    st.write("---")
    st.subheader("📸 " + L["photo_gallery"])
    if st.button(L["show_images"]):
        query = sel_name + " Oman"
        urls = fetch_images_from_backend(query, per=img_count)
        if not urls:
            urls = unsplash_fallback(query, per=img_count)
        # show images (download bytes and display)
        cols = st.columns(3)
        shown = 0
        for i, u in enumerate(urls):
            if shown >= img_count: break
            b = fetch_image_bytes(u)
            if not b:
                continue
            try:
                image = Image.open(BytesIO(b)).convert("RGB")
                with cols[shown % 3]:
                    st.image(image, use_container_width=True, caption=sel_name)
                shown += 1
            except Exception:
                try:
                    with cols[shown % 3]:
                        st.image(b, use_container_width=True, caption=sel_name)
                    shown += 1
                except Exception:
                    continue
        if shown == 0:
            st.info(L["no_photos"])

# ---- right: details + reddit ----
with col_right:
    st.subheader("📍 " + (sel_item["name_en"] if lang=="en" else sel_item["name_ar"]))
    st.markdown(f"**{L['region']}:** {sel_region}")
    st.markdown(f"**{L['coords']}:** {sel_lat}, {sel_lon}")
    st.write("---")
    st.subheader("🔊 " + L["community_buzz"])
    topic = st.text_input("Topic / الموضوع", sel_name)
    if st.button(L["fetch_reddit"]):
        # prefer backend reddit endpoint
        posts = []
        try:
            r = requests.get(f"{BACKEND_URL}/reddit", params={"topic": topic, "limit": 6}, timeout=8)
            if r.ok:
                data = r.json()
                posts = data.get("posts") or data.get("results") or data.get("items") or data.get("data") or []
        except Exception:
            posts = []
        # fallback: try Reddit's JSON (less reliable from browser but we try)
        if not posts:
            try:
                r2 = requests.get(f"https://www.reddit.com/search.json?q={quote_plus(topic)}&limit=6", headers={"User-Agent":"OmanVista/1.0"}, timeout=8)
                if r2.ok:
                    js = r2.json()
                    for ch in js.get("data",{}).get("children",[]):
                        d = ch.get("data",{})
                        posts.append({"title": d.get("title"), "link": "https://reddit.com"+d.get("permalink","")})
            except Exception:
                posts = posts or []
        if not posts:
            st.info(L["no_posts"])
        else:
            for p in posts[:6]:
                title = p.get("title") if isinstance(p, dict) else str(p)
                link = p.get("link") or p.get("url") or "#"
                st.markdown(f"- [{title}]({link})")

st.write("---")
st.markdown("<div style='text-align:center;color:#777'>Made with ❤️ — Golden Bird</div>", unsafe_allow_html=True)
