# fronted/app.py
import streamlit as st
import requests
import folium
import streamlit.components.v1 as components
from io import BytesIO
from urllib.parse import quote_plus
from PIL import Image

# ---------------- page setup ----------------
st.set_page_config(page_title="OmanVista", layout="wide")
PRIMARY = "#006666"

# ---------------- background (optional) ----------------
def set_background():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
            background-size: cover;
            background-attachment: fixed;
        }}
        /* make cards readable on background */
        .stBlock {{
            background: rgba(255,255,255,0.88);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

set_background()

# ---------------- backend config ----------------
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://fortunate-rebirth-production-93ce.up.railway.app")

# ---------------- helpers ----------------
@st.cache_data(ttl=600)
def fetch_image_bytes(url: str):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.content
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_images_from_backend(query: str, per: int = 6):
    """Try backend first. Return list of image URLs (strings)."""
    urls = []
    try:
        r = requests.get(f"{BACKEND_URL}/images?q={quote_plus(query)}&per={per}", timeout=8)
        if r.ok:
            data = r.json()
            # look for common keys that hold lists
            for key in ("images", "results", "photos", "items", "data"):
                if isinstance(data.get(key), list):
                    items = data.get(key)
                    for it in items:
                        # if it's a string
                        if isinstance(it, str):
                            urls.append(it)
                        elif isinstance(it, dict):
                            # common structures
                            for k in ("url","src","image","link","regular","original","large","medium"):
                                if it.get(k):
                                    # nested src dict
                                    if isinstance(it.get(k), dict):
                                        # take first good value
                                        for kk in ("large","medium","original","regular"):
                                            if it[k].get(kk):
                                                urls.append(it[k][kk]); break
                                    else:
                                        urls.append(it.get(k))
                                        break
                            # special for pexels: it['src']['large']
                            if not urls and it.get("src") and isinstance(it["src"], dict):
                                for kk in ("large","medium","original"):
                                    if it["src"].get(kk):
                                        urls.append(it["src"][kk]); break
            # also allow top-level list of urls
            if not urls and isinstance(data, list):
                for it in data:
                    if isinstance(it, str):
                        urls.append(it)
            # fallback: maybe backend returns {"images": ["url1","url2"]}
            if urls:
                return urls[:per]
    except Exception:
        return []
    return []

def unsplash_fallback(query: str, per: int = 6):
    """Generate source.unsplash.com URLs as fallback."""
    return [f"https://source.unsplash.com/800x600/?{quote_plus(query)}&sig={i}" for i in range(per)]

# ---------------- header ----------------
st.title("🌍 OmanVista - AI Tourism Explorer")
st.markdown("Discover hidden gems of Oman — maps, images and community buzz.")

# ---------------- backend check ----------------
col_status = st.container()
with col_status:
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=5)
        if r.ok:
            st.success("✅ Backend is connected")
        else:
            st.warning("⚠️ Backend responded but not OK")
    except Exception as e:
        st.error(f"❌ Backend not reachable: {e}")

st.write("---")

# ---------------- attractions (static) ----------------
ATTRACTIONS = [
    {"id":"sultan_qaboos","name":"Sultan Qaboos Grand Mosque","lat":23.5859,"lon":58.4078,"region":"Muscat"},
    {"id":"mutrah","name":"Mutrah Corniche","lat":23.6155,"lon":58.5638,"region":"Muscat"},
    {"id":"nizwa","name":"Nizwa Fort","lat":22.9333,"lon":57.5333,"region":"Ad Dakhiliyah"},
    {"id":"jebel_shams","name":"Jebel Shams","lat":23.2386,"lon":57.2742,"region":"Ad Dakhiliyah"},
    {"id":"wadi_shab","name":"Wadi Shab","lat":22.8861,"lon":59.0136,"region":"Ash Sharqiyah"},
]

# sidebar selection
st.sidebar.header("Explore / استكشاف")
place_names = [p["name"] for p in ATTRACTIONS]
sel_idx = st.sidebar.selectbox("Choose a place", range(len(place_names)), format_func=lambda i: place_names[i])
sel = ATTRACTIONS[sel_idx]

# ---------------- map (stable render) ----------------
st.subheader("🗺️ Map")
if st.button("Show Map"):
    # create folium map
    m = folium.Map(location=[sel["lat"], sel["lon"]], zoom_start=11)
    # add markers
    for a in ATTRACTIONS:
        folium.Marker([a["lat"], a["lon"]], popup=a["name"]).add_to(m)
    # highlight selected
    folium.CircleMarker([sel["lat"], sel["lon"]], radius=8, color="#ff5722", fill=True, fill_color="#ff5722").add_to(m)
    # render HTML and keep it persistent
    html = m.get_root().render()
    components.html(html, height=520)

st.write("---")

# ---------------- images (backend -> fallback) ----------------
st.subheader("📸 Photo Gallery")
if st.button("Show Images"):
    query = sel["name"] + " Oman"
    urls = get_images_from_backend(query, per=6)
    if not urls:
        urls = unsplash_fallback(query, per=6)
    # fetch bytes and show
    cols = st.columns(3)
    shown = 0
    for i, u in enumerate(urls):
        if shown >= 6: break
        b = fetch_image_bytes(u)
        if b:
            try:
                img = Image.open(BytesIO(b))
                with cols[shown % 3]:
                    st.image(img, use_column_width=True, caption=sel["name"])
                shown += 1
            except Exception:
                # if PIL fails, try st.image using raw bytes
                try:
                    with cols[shown % 3]:
                        st.image(b, use_column_width=True, caption=sel["name"])
                    shown += 1
                except Exception:
                    continue
    if shown == 0:
        st.info("No images to display.")

st.write("---")

# ---------------- quick info & reddit placeholder ----------------
st.subheader("🔎 Quick info")
st.markdown(f"- **Place:** {sel['name']}")
st.markdown(f"- **Coordinates:** {sel['lat']}, {sel['lon']}")
st.markdown(f"- **Region:** {sel['region']}")

st.subheader("🔊 Community Buzz (Reddit)")
topic = st.text_input("Topic", sel["name"])
if st.button("Fetch Posts"):
    try:
        r = requests.get(f"{BACKEND_URL}/reddit?topic={quote_plus(topic)}&limit=6", timeout=8)
        if r.ok:
            data = r.json()
            posts = data.get("posts", [])
            if posts:
                for p in posts:
                    t = p.get("title") if isinstance(p, dict) else str(p)
                    l = p.get("link", "#") if isinstance(p, dict) else "#"
                    st.markdown(f"- [{t}]({l})")
            else:
                st.info("No posts found.")
        else:
            st.error("Failed to fetch reddit feed from backend.")
    except Exception as e:
        st.error(f"Error: {e}")

st.write("---")
st.markdown("<div style='text-align:center;color:#777'>Made with ❤️ — Golden Bird</div>", unsafe_allow_html=True)
