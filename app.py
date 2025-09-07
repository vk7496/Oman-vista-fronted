
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from urllib.parse import quote_plus
from PIL import Image
from io import BytesIO

# ---------- Config ----------
# Set this secret in Streamlit Cloud as "BACKEND_URL" (e.g. https://fortunate-rebirth-production-93ce.up.railway.app)
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://fortunate-rebirth-production-93ce.up.railway.app")

# UI colors / style
PRIMARY = "#006666"

# ---------- Language pack ----------
LANG = st.sidebar.radio("🌐 Language | اللغة", ["English", "العربية"], index=0)

TXT = {
    "title": {"English": "OmanVista — AI Tourism Explorer", "العربية": "عُمان فيستا — مستكشف السياحة بالذكاء الاصطناعي"},
    "subtitle": {
        "English": "Discover Oman’s hidden gems — maps, images and community buzz.",
        "العربية": "اكتشف جواهر عُمان — خرائط، صور وحديث المجتمع."
    },
    "select_place": {"English": "Choose a place", "العربية": "انتخاب مکان"},
    "show_images": {"English": "Show Images", "العربية": "نمایش تصاویر"},
    "show_map": {"English": "Show Map", "العربية": "نمایش نقشه"},
    "fetch_reddit": {"English": "Fetch Reddit Posts", "العربية": "جلب پست‌های Reddit"},
    "backend_connected": {"English": "✅ Backend is connected", "العربية": "✅ ارتباط با بک‌اند برقرار شد"},
    "backend_failed": {"English": "❌ Backend not responding", "العربية": "❌ بک‌اند پاسخگو نیست"},
    "gallery_title": {"English": "Photo Gallery", "العربية": "گالری تصاویر"},
    "reddit_title": {"English": "Community Buzz (Reddit)", "العربية": "گفتمان جامعه (Reddit)"},
}

# ---------- Page config ----------
st.set_page_config(page_title="OmanVista", page_icon="🌍", layout="wide")

# ---------- Header ----------
st.markdown(
    f"<h1 style='color:{PRIMARY}; font-weight:800'>{TXT['title'][LANG]}</h1>",
    unsafe_allow_html=True
)
st.markdown(f"<p style='color:#333'>{TXT['subtitle'][LANG]}</p>", unsafe_allow_html=True)
st.write("---")

# ---------- Check backend ----------
def check_backend():
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=6)
        return r.ok
    except Exception:
        return False

if check_backend():
    st.success(TXT["backend_connected"][LANG])
else:
    st.error(TXT["backend_failed"][LANG])
    st.stop()

# ---------- Static attractions list (with coords + short) ----------
ATTRACTIONS = [
    {"id":"wadi_shab","name_en":"Wadi Shab","name_ar":"وادی شاب","lat":22.8861,"lon":59.0136,"desc_en":"A beautiful valley with turquoise pools and waterfalls.","desc_ar":"دره‌ای زیبا با حوضچه‌ها و آبشارها"},
    {"id":"jebel_akhdar","name_en":"Jebel Akhdar","name_ar":"جبل الأخضر","lat":23.0771,"lon":57.4140,"desc_en":"The Green Mountain, terraced farms & cool weather.","desc_ar":"کوه سبز، مزارع تراس دار و آب و هوای خنک"},
    {"id":"mutrah","name_en":"Mutrah Corniche","name_ar":"كورنيش مطرح","lat":23.6160,"lon":58.5430,"desc_en":"Seaside promenade and historic souq.","desc_ar":"پیاده‌رو ساحلی و بازار تاریخی"},
    {"id":"sultan_qaboos","name_en":"Sultan Qaboos Grand Mosque","name_ar":"جامع السلطان قابوس","lat":23.5859,"lon":58.4078,"desc_en":"Landmark mosque with beautiful architecture.","desc_ar":"مسجد نمادین با معماری زیبا"},
    {"id":"nizwa","name_en":"Nizwa Fort","name_ar":"قلعة نزوى","lat":22.9333,"lon":57.5333,"desc_en":"Historic fort and old market.","desc_ar":"قلعه تاریخی و بازار قدیمی"}
]

# ---------- Sidebar: filters ----------
st.sidebar.header("Explore / استكشاف")
place_names = [p["name_en"] if LANG=="English" else p["name_ar"] for p in ATTRACTIONS]
sel_place_idx = st.sidebar.selectbox(TXT["select_place"][LANG], range(len(place_names)), format_func=lambda i: place_names[i])
sel_place = ATTRACTIONS[sel_place_idx]

# ---------- Main layout: two columns ----------
col1, col2 = st.columns([2,1])

# ----- left: map + buttons -----
with col1:
    st.subheader("🗺️ " + ( "Map" if LANG=="English" else "الخريطة" ))
    if st.button(TXT["show_map"][LANG]):
        # Create a folium map centered near selected place (zoomed)
        m = folium.Map(location=[sel_place["lat"], sel_place["lon"]], zoom_start=10)
        # add markers for all attractions
        for a in ATTRACTIONS:
            popup_txt = a["name_en"] if LANG=="English" else a["name_ar"]
            folium.Marker([a["lat"], a["lon"]], popup=popup_txt).add_to(m)
        # add a marker for selected place with different color
        folium.CircleMarker([sel_place["lat"], sel_place["lon"]],
                            radius=8, color="#ff5722", fill=True, fill_color="#ff5722",
                            popup=(sel_place["name_en"] if LANG=="English" else sel_place["name_ar"])
                           ).add_to(m)
        st_data = st_folium(m, width="100%", height=600)

    st.write("---")
    st.subheader("📸 " + (TXT["gallery_title"][LANG] if LANG=="English" else TXT["gallery_title"][LANG]))

    # Show images button & gallery
    if st.button(TXT["show_images"][LANG]):
        q = sel_place["name_en"] if LANG=="English" else sel_place["name_ar"]
        try:
            r = requests.get(f"{BACKEND_URL}/images?q={quote_plus(q)}&per=6", timeout=10)
            if r.status_code == 200:
                data = r.json()
                imgs = data.get("images") or data.get("results") or data.get("images", [])
                # Backend payloads may differ; try keys
                if not imgs and isinstance(data.get("images"), list):
                    imgs = data.get("images")
                # try reddit style
                # if payload shape is {source, images}
                if not imgs:
                    # try fallback keys
                    for k in ("results","images","images_list"):
                        if isinstance(data.get(k), list):
                            imgs = data.get(k)
                            break
                if not imgs:
                    # try if backend returned "images" as list of URLs
                    imgs = data.get("images") or []
                # Display gallery
                if isinstance(imgs, list) and len(imgs)>0:
                    cols = st.columns(3)
                    for i, img in enumerate(imgs[:9]):
                        url = None
                        # img can be dict or string
                        if isinstance(img, dict):
                            # look common fields
                            url = img.get("url") or img.get("src") or img.get("image") or img.get("src_large") or img.get("original")
                        elif isinstance(img, str):
                            url = img
                        if not url:
                            # if backend returned plain URLs under key 'images'
                            url = img if isinstance(img, str) else None
                        if url:
                            try:
                                resp = requests.get(url, timeout=8)
                                img_obj = Image.open(BytesIO(resp.content))
                                with cols[i % 3]:
                                    st.image(img_obj, use_column_width=True, caption=f"{sel_place['name_en'] if LANG=='English' else sel_place['name_ar']}")
                            except Exception:
                                pass
                else:
                    st.info("No images returned.")
            else:
                st.error("Failed to fetch images from backend.")
        except Exception as e:
            st.error(f"Error fetching images: {e}")

# ----- right: attraction details & reddit -----
with col2:
    st.subheader("📍 " + (sel_place["name_en"] if LANG=="English" else sel_place["name_ar"]))
    st.write(sel_place["desc_en"] if LANG=="English" else sel_place["desc_ar"])
    st.write("---")
    st.subheader("🔎 " + ( "Quick info" if LANG=="English" else "معلومات سریع" ))
    st.markdown(f"- {('Region:' if LANG=='English' else 'المنطقة:')} {sel_place.get('region','-')}")
    st.markdown(f"- {('Coordinates:' if LANG=='English' else 'مختصات:')} {sel_place['lat']}, {sel_place['lon']}")

    st.write("---")
    st.subheader("🔊 " + TXT["reddit_title"][LANG])
    topic = st.text_input("Topic | الموضوع", sel_place["name_en"] if LANG=="English" else sel_place["name_ar"])
    if st.button(TXT["fetch_reddit"][LANG]):
        try:
            r = requests.get(f"{BACKEND_URL}/reddit?topic={quote_plus(topic)}&limit=6", timeout=10)
            if r.status_code == 200:
                posts = r.json().get("posts", [])
                if posts:
                    for p in posts:
                        title = p.get("title") if isinstance(p, dict) else str(p)
                        link = p.get("link") if isinstance(p, dict) else "#"
                        st.markdown(f"- [{title}]({link})")
                else:
                    st.info("No recent posts found.")
            else:
                st.error("Failed to fetch Reddit feed.")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------- Footer ----------
st.write("---")
st.markdown(f"<div style='text-align:center;color:#777'>Made with ❤️ in Oman — Golden Bird</div>", unsafe_allow_html=True)
