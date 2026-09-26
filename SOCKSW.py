# SOCKSW.py
import streamlit as st
import os
import io
import base64
import requests
from PIL import Image, ImageOps

# ==================== 設定 ====================
API_BASE = os.environ.get("API_BASE", "https://socksql-1.onrender.com")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
PRODUCT_IMAGES = {f"product{i}": f"product{i}.jpg" for i in range(1, 11)}
DUCK_IMAGE = "duck.jpg"

st.set_page_config(
    page_title="Gabriel-JL Co., Ltd. | SOCKS",
    page_icon="🧦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================== API ====================
def api_get_messages(limit=50):
    try:
        r = requests.get(f"{API_BASE}/api/messages",
                         params={"limit": limit}, timeout=8)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else []
    except Exception:
        return []


def api_post_message(name, email, message):
    try:
        r = requests.post(f"{API_BASE}/api/messages",
                          json={"name": name, "email": email, "message": message},
                          timeout=8)
        return r.status_code in (200, 201)
    except Exception:
        return False


def api_get_visits():
    try:
        r = requests.get(f"{API_BASE}/api/visits", timeout=8)
        r.raise_for_status()
        return r.json().get("count", 0)
    except Exception:
        return 0


def api_inc_visits():
    try:
        r = requests.post(f"{API_BASE}/api/visits", timeout=8)
        r.raise_for_status()
        return r.json().get("count", 0)
    except Exception:
        return 0


# ==================== 圖片工具 ====================
def img_to_b64(path, max_side=400):
    if not os.path.exists(path):
        return None, None
    try:
        img = Image.open(path)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        if max(img.size) > max_side:
            ratio = max_side / max(img.size)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                             Image.LANCZOS)
        buf = io.BytesIO()
        if img.mode == "RGBA":
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode(), "image/png"
        img.save(buf, format="JPEG", quality=88)
        return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"
    except Exception as e:
        print("img_to_b64 error:", path, e)
        return None, None


def duck_transparent_b64(path, max_side=500, black_cutoff=100,
                         rotate_deg=90, padding=20):
    if not os.path.exists(path):
        return None, None
    try:
        img = Image.open(path)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")

        if rotate_deg == 90:
            img = img.rotate(90, expand=True)
        elif rotate_deg == -90:
            img = img.rotate(-90, expand=True)
        elif rotate_deg == 180:
            img = img.rotate(180, expand=True)

        if max(img.size) > max_side:
            ratio = max_side / max(img.size)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                             Image.LANCZOS)

        w, h = img.size
        px = img.load()
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        out_px = out.load()

        for y in range(h):
            for x in range(w):
                r, g, b = px[x, y]
                brightness = (r + g + b) // 3
                if brightness < black_cutoff:
                    alpha = int(255 * (1 - brightness / black_cutoff))
                    alpha = max(0, min(255, alpha))
                    out_px[x, y] = (0, 0, 0, alpha)
                else:
                    out_px[x, y] = (0, 0, 0, 0)

        bbox = out.getbbox()
        if bbox:
            left, top, right, bottom = bbox
            left   = max(0, left - padding)
            top    = max(0, top - padding)
            right  = min(w, right + padding)
            bottom = min(h, bottom + padding)
            out = out.crop((left, top, right, bottom))

        buf = io.BytesIO()
        out.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode(), "image/png"
    except Exception as e:
        print("duck_transparent_b64 error:", path, e)
        return None, None


duck_path = os.path.join(IMAGE_DIR, DUCK_IMAGE)
duck_b64, duck_mime = duck_transparent_b64(
    duck_path, max_side=500, black_cutoff=100, rotate_deg=90, padding=20
)
if duck_b64:
    duck_src = f"data:{duck_mime};base64,{duck_b64}"
    ducks_html = (
        f'<img src="{duck_src}" class="duck-img duck-1" alt="duck1">'
        f'<img src="{duck_src}" class="duck-img duck-2" alt="duck2">'
        f'<img src="{duck_src}" class="duck-img duck-3" alt="duck3">'
        f'<img src="{duck_src}" class="duck-img duck-4" alt="duck4">'
    )
else:
    ducks_html = ""


# ==================== CSS ====================
CSS = """
<style>
* { font-family: 'Helvetica Neue', 'Microsoft YaHei', sans-serif; }
html, body { -webkit-text-size-adjust: 100%; }
.block-container { padding: 1rem 1rem 0 1rem !important; max-width: 100% !important; }

.header-banner {
    position: relative;
    background: linear-gradient(135deg, #a8b8e8 0%, #b8a8e0 50%, #9fa8e0 100%);
    padding: 0.5rem 1rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(168,184,232,0.4);
    overflow: hidden;
    min-height: 70px;
    padding-right: 260px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.header-banner .duck-img {
    position: absolute;
    width: auto;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    box-shadow: none !important;
    outline: none !important;
    object-fit: contain;
}
.header-banner .duck-1 {
    height: 50px; top: 10px; right: 180px; z-index: 14;
    animation: duckWalk 3s ease-in-out infinite;
}
.header-banner .duck-2 {
    height: 36px; top: 20px; right: 130px; z-index: 12;
    animation: duckWalk 3s ease-in-out infinite 0.4s;
}
.header-banner .duck-3 {
    height: 24px; top: 30px; right: 88px; z-index: 10;
    animation: duckWalk 3s ease-in-out infinite 0.8s;
}
.header-banner .duck-4 {
    height: 14px; top: 42px; right: 56px; z-index: 8;
    animation: duckWalk 3s ease-in-out infinite 1.2s;
}
@keyframes duckWalk {
    0%,100% { transform: translateX(0); }
    50%     { transform: translateX(12px); }
}
.header-banner h1 {
    color: #fff; font-size: 1.3rem; margin: 0;
    letter-spacing: 1px; position: relative; z-index: 20;
    text-align: left; line-height: 1.3;
}
.header-banner p {
    color: #fff; font-size: 0.9rem; margin-top: 0.25rem;
    font-weight: 300; position: relative; z-index: 20;
    text-align: left;
}
.visit-counter {
    display: inline-flex; align-items: center; gap: 0.6rem;
    background: rgba(255,255,255,0.85); border: 2px solid #1a1a1a;
    border-radius: 40px; padding: 0.4rem 1.2rem;
    font-family: monospace; font-size: 1rem; color: #1a1a1a;
    margin-bottom: 1rem;
}
.visit-counter .num { font-weight: 700; font-size: 1.4rem; color: #000; }
.product-card {
    background: #fff; border-radius: 12px; padding: 1rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    margin-bottom: 1rem; border: 1px solid #f0f0f0;
}
.product-card .price { color: #e94560; font-size: 1.3rem; font-weight: bold; }
.product-card .desc { color: #555; font-size: 0.95rem; line-height: 1.6; }
.contact-card {
    background: linear-gradient(135deg, #0f3460, #16213e);
    color: #fff; border-radius: 12px; padding: 2rem; text-align: center;
}
.contact-card a { color: #e94560; text-decoration: none; }
.msg-card {
    background: #fff; border-radius: 10px; padding: 0.8rem 1rem;
    margin-bottom: 0.8rem; border-left: 4px solid #a8b8e8;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.msg-card .msg-name { font-weight: 600; color: #16213e; font-size: 0.95rem; }
.msg-card .msg-time { color: #999; font-size: 0.78rem; margin-left: 0.5rem; }
.msg-card .msg-body {
    color: #333; font-size: 0.92rem; margin-top: 0.35rem;
    line-height: 1.55; white-space: pre-wrap; word-break: break-word;
}
#MainMenu, footer { visibility: hidden; }

@media (max-width: 768px) {
    .header-banner {
        min-height: 62px;
        padding: 0.5rem 0.7rem;
        padding-right: 170px;
    }
    .header-banner h1 { font-size: 1.0rem; line-height: 1.25; }
    .header-banner p  { font-size: 0.7rem; }
    .header-banner .duck-1 { height: 36px; top: 8px;  right: 115px; }
    .header-banner .duck-2 { height: 26px; top: 16px; right: 80px;  }
    .header-banner .duck-3 { height: 17px; top: 26px; right: 48px;  }
    .header-banner .duck-4 { height: 10px; top: 36px; right: 24px;  }
    .visit-counter { font-size: 0.9rem; padding: 0.35rem 0.9rem; }
    .visit-counter .num { font-size: 1.15rem; }
    .product-card { padding: 0.8rem; }
    .product-card .price { font-size: 1.15rem; }
    .product-card .desc  { font-size: 0.9rem; }
    .contact-card { padding: 1.2rem; }
    .block-container { padding: 0.6rem 0.6rem 0 0.6rem !important; }
}

@media (max-width: 480px) {
    .header-banner {
        min-height: 56px;
        padding: 0.45rem 0.6rem;
        padding-right: 130px;
        border-radius: 10px;
    }
    .header-banner h1 { font-size: 0.9rem; line-height: 1.2; }
    .header-banner p  { font-size: 0.6rem; margin-top: 0.1rem; }
    .header-banner .duck-1 { height: 28px; top: 6px;  right: 88px; }
    .header-banner .duck-2 { height: 20px; top: 15px; right: 60px; }
    .header-banner .duck-3 { height: 13px; top: 25px; right: 36px; }
    .header-banner .duck-4 { height: 8px;  top: 35px; right: 18px; }
    .visit-counter { font-size: 0.82rem; padding: 0.3rem 0.8rem; gap: 0.4rem; }
    .visit-counter .num { font-size: 1.05rem; }
    .product-card { padding: 0.7rem; border-radius: 10px; }
    .product-card .price { font-size: 1.05rem; }
    .product-card .desc  { font-size: 0.85rem; }
    .contact-card { padding: 1rem; border-radius: 10px; }
    .msg-card { padding: 0.6rem 0.8rem; }
    .msg-card .msg-name { font-size: 0.9rem; }
    .msg-card .msg-time { font-size: 0.72rem; }
    .msg-card .msg-body { font-size: 0.86rem; }
    .block-container { padding: 0.5rem 0.5rem 0 0.5rem !important; }
}

@media (max-width: 380px) {
    .header-banner { min-height: 52px; padding-right: 115px; }
    .header-banner h1 { font-size: 0.82rem; }
    .header-banner p  { font-size: 0.55rem; }
    .header-banner .duck-1 { height: 24px; top: 6px;  right: 78px; }
    .header-banner .duck-2 { height: 17px; top: 15px; right: 52px; }
    .header-banner .duck-3 { height: 11px; top: 25px; right: 30px; }
    .header-banner .duck-4 { height: 7px;  top: 34px; right: 14px; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ==================== 雙語字典 ====================
TEXTS = {
    "en": {
        "title": "Gabriel-JL Co., Ltd.",
        "subtitle": "Premium SOCKS Manufacturer & Supplier",
        "nav_products": "🧦 Products",
        "nav_about": "ℹ️ About Us",
        "nav_contact": "📬 Contact / Message",
        "products_title": "Our SOCKS Collection",
        "products_desc": "High-quality socks for every occasion — sports, casual, business, and custom designs.",
        "about_title": "About Gabriel-JL Co., Ltd.",
        "about_text": "**Gabriel-JL Co., Ltd.** (Contact: He YA) is a professional manufacturer and exporter of all kinds of socks.\n\nWe specialize in:\n- 🏃 Sports socks (running, basketball, cycling)\n- 👔 Business & dress socks\n- 🧦 Casual & fashion socks\n- 🏭 Custom OEM/ODM orders\n- 🌿 Organic cotton & bamboo fiber socks\n\n**Email:** hejingling51@gmail.com",
        "contact_title": "Send Us a Message",
        "contact_desc": "We'd love to hear from you! Leave your message below and we'll get back to you within 24 hours.",
        "form_name": "Your Name",
        "form_email": "Your Email",
        "form_message": "Your Message",
        "form_submit": "Send Message",
        "form_success": "✅ Thank you! Your message has been received. We'll contact you soon.",
        "form_error": "⚠️ Please fill in all fields.",
        "api_error": "⚠️ Failed to send, please try again later.",
        "guestbook_recent": "Recent Messages",
        "guestbook_empty": "No messages yet. Be the first to leave one!",
        "advantages_title": "Our Advantages",
        "advantages": [
            ("✅", "Quality Control", "Strict QC at every step"),
            ("🚚", "Fast Delivery", "Worldwide shipping"),
            ("💰", "Competitive Price", "Factory direct pricing"),
            ("🎨", "Custom Design", "OEM/ODM welcomed"),
        ],
        "no_photo": "Photo coming soon",
        "photo_hint": "Put your product photos into the `images/` folder with these names:",
        "cat_all": "🧦 All Products",
        "cat_children": "🧒 Children SOCKS",
        "cat_adult": "🧑 Adult SOCKS",
        "cat_label": "Category",
        "lang_switch": "🇨🇳 中文",
        "footer": "© 2025 Gabriel-JL Co., Ltd. All rights reserved. | Contact: He YA | hejingling51@gmail.com",
        "products": [
            ("product1",  "Sports Socks",      "Breathable, moisture-wicking, cushioned sole. Perfect for running and outdoor activities.", "$2.50 - $4.00 / pair", "🏃", "adult"),
            ("product2",  "Business Socks",    "Elegant design, premium cotton blend. Comfortable for all-day office wear.",             "$3.00 - $5.00 / pair", "👔", "adult"),
            ("product3",  "Casual Socks",      "Soft, colorful, and stylish. Great for everyday wear and gifts.",                       "$1.80 - $3.00 / pair", "🧦", "adult"),
            ("product4",  "Custom OEM Socks",  "Your logo, your design, your colors. MOQ from 500 pairs. Free sample available.",       "Negotiable",           "🎨", "adult"),
            ("product5",  "Ankle Socks",       "Low-cut, invisible design. Perfect for sneakers and casual shoes.",                     "$1.50 - $2.60 / pair", "👟", "adult"),
            ("product6",  "Kids Socks",        "Soft and safe for children. Various cute designs available.",                           "$1.50 - $2.50 / pair", "🧒", "children"),
            ("product7",  "Baby Socks",        "Ultra-soft cotton for newborns. Anti-slip sole and gentle elastic band.",                "$1.20 - $2.00 / pair", "👶", "children"),
            ("product8",  "School Socks",      "Durable knee-high socks for school uniforms. Easy to wash and keep white.",              "$1.60 - $2.80 / pair", "🎒", "children"),
            ("product9",  "Toddler Socks",     "Fun cartoon patterns for toddlers. Non-slip grip and breathable fabric.",                "$1.30 - $2.20 / pair", "🧸", "children"),
            ("product10", "Teen Sports Socks", "Athletic socks for teenagers. Cushioned, durable, and colorful.",                        "$2.00 - $3.50 / pair", "⚽", "children"),
        ],
    },
    "zh": {
        "title": "Gabriel-JL 有限公司",
        "subtitle": "專業襪子製造商與供應商",
        "nav_products": "🧦 產品展示",
        "nav_about": "ℹ️ 關於我們",
        "nav_contact": "📬 聯絡我們 / 留言",
        "products_title": "我們的襪子系列",
        "products_desc": "高品質襪子，適合各種場合 — 運動、休閒、商務及訂製設計。",
        "about_title": "關於 Gabriel-JL 有限公司",
        "about_text": "**Gabriel-JL 有限公司**（聯絡人：He YA）是一家專業的襪子製造商和出口商。\n\n我們專注於：\n- 🏃 運動襪（跑步、籃球、騎行）\n- 👔 商務正裝襪\n- 🧦 休閒時尚襪\n- 🏭 訂製 OEM/ODM 訂單\n- 🌿 有機棉與竹纖維襪\n\n**郵箱：** hejingling51@gmail.com",
        "contact_title": "給我們留言",
        "contact_desc": "歡迎聯絡我們！請在下方留言，我們會在24小時內回覆您。",
        "form_name": "您的姓名",
        "form_email": "您的郵箱",
        "form_message": "您的留言",
        "form_submit": "發送留言",
        "form_success": "✅ 感謝您！我們已收到您的留言，會盡快與您聯絡。",
        "form_error": "⚠️ 請填寫所有欄位。",
        "api_error": "⚠️ 系統暫時無法送出留言，請稍後再試。",
        "guestbook_recent": "近期留言",
        "guestbook_empty": "暫無留言，歡迎成為第一個留言的人！",
        "advantages_title": "我們的優勢",
        "advantages": [
            ("✅", "品質把控", "每一步嚴格質檢"),
            ("🚚", "快速交付", "全球發貨"),
            ("💰", "價格優勢", "工廠直銷價格"),
            ("🎨", "訂製設計", "歡迎OEM/ODM"),
        ],
        "no_photo": "照片即將上傳",
        "photo_hint": "請將您的產品照片放入 `images/` 資料夾，檔名如下：",
        "cat_all": "🧦 全部產品",
        "cat_children": "🧒 兒童襪",
        "cat_adult": "🧑 成人襪",
        "cat_label": "產品分類",
        "lang_switch": "🇬🇧 English",
        "footer": "© 2025 Gabriel-JL 有限公司 版權所有 | 聯絡人: He YA | hejingling51@gmail.com",
        "products": [
            ("product1",  "運動襪",         "透氣吸汗，加厚緩衝鞋底。適合跑步、健身及戶外運動。", "$2.50 - $4.00 / 雙", "🏃", "adult"),
            ("product2",  "商務襪",         "優雅設計，優質棉混紡。適合全天辦公穿著，舒適有型。", "$3.00 - $5.00 / 雙", "👔", "adult"),
            ("product3",  "休閒襪",         "柔軟多彩，時尚百搭。適合日常穿著和送禮。",           "$1.80 - $3.00 / 雙", "🧦", "adult"),
            ("product4",  "訂製 OEM 襪子",  "您的Logo、您的設計、您的顏色。起訂量500雙起，可提供免費樣品。", "面議",           "🎨", "adult"),
            ("product5",  "船襪 / 隱形襪",  "低筒隱形設計。完美搭配運動鞋與休閒鞋。",             "$1.50 - $2.60 / 雙", "👟", "adult"),
            ("product6",  "兒童襪",         "柔軟安全，適合兒童。多款可愛設計可選。",             "$1.50 - $2.50 / 雙", "🧒", "children"),
            ("product7",  "嬰兒襪",         "超柔軟純棉，適合新生兒。防滑鞋底與溫和鬆緊帶。",     "$1.20 - $2.00 / 雙", "👶", "children"),
            ("product8",  "學生襪",         "耐穿及膝襪，適合校服。易洗滌、常保潔白。",           "$1.60 - $2.80 / 雙", "🎒", "children"),
            ("product9",  "幼兒襪",         "趣味卡通圖案，適合幼兒。防滑設計、透氣材質。",       "$1.30 - $2.20 / 雙", "🧸", "children"),
            ("product10", "青少年運動襪",   "適合青少年的運動襪。加厚耐穿、色彩活潑。",           "$2.00 - $3.50 / 雙", "⚽", "children"),
        ],
    },
}


# ==================== Session State ====================
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "form_status" not in st.session_state:
    st.session_state.form_status = None
if "category" not in st.session_state:
    st.session_state.category = "all"
if "visited" not in st.session_state:
    st.session_state.visited = True
    visit_count = api_inc_visits()
else:
    visit_count = api_get_visits()


def toggle_lang():
    st.session_state.lang = "zh" if st.session_state.lang == "en" else "en"


def handle_form_submit():
    name = st.session_state.get("input_name", "").strip()
    email = st.session_state.get("input_email", "").strip()
    message = st.session_state.get("input_message", "").strip()
    if not name or not email or not message:
        st.session_state.form_status = "error"
        return
    if api_post_message(name, email, message):
        st.session_state.form_status = "success"
        for k in ("input_name", "input_email", "input_message"):
            if k in st.session_state:
                del st.session_state[k]
    else:
        st.session_state.form_status = "api_error"


T = TEXTS[st.session_state.lang]


# ==================== 頂部橫幅 ====================
banner_html = (
    '<div class="header-banner">' + ducks_html +
    '<h1>' + T["title"] + '</h1>' +
    '<p>' + T["subtitle"] + '</p>' +
    '</div>'
)
st.markdown(banner_html, unsafe_allow_html=True)

counter_html = (
    '<div class="visit-counter">'
    '<span>👀 瀏覽次數</span>'
    '<span class="num">' + str(visit_count) + '</span>'
    '</div>'
)
st.markdown(counter_html, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 6, 1])
with col3:
    if st.button(T["lang_switch"], key="lang_btn"):
        toggle_lang()
        st.rerun()


# ==================== 側邊欄 ====================
with st.sidebar:
    st.markdown("### 🧦 " + T["title"])
    st.markdown("---")
    page = st.radio(
        "Navigation",
        [T["nav_products"], T["nav_about"], T["nav_contact"]],
        label_visibility="collapsed",
    )
    if page == T["nav_products"]:
        st.markdown("---")
        st.markdown("**" + T["cat_label"] + "**")
        cat_options = {"all": T["cat_all"], "children": T["cat_children"], "adult": T["cat_adult"]}
        cat_keys = list(cat_options.keys())
        cat_labels = list(cat_options.values())
        try:
            current_idx = cat_keys.index(st.session_state.category)
        except ValueError:
            current_idx = 0
        selected_label = st.radio("Category", cat_labels, index=current_idx,
                                   label_visibility="collapsed", key="cat_radio")
        st.session_state.category = cat_keys[cat_labels.index(selected_label)]

    st.markdown("---")
    st.markdown("**📧 Email:**  \nhejingling51@gmail.com")
    st.markdown("**👤 Contact:**  \nHe YA")
    st.markdown("---")
    st.caption("Gabriel-JL Co., Ltd.")


# ==================== 留言板共用 ====================
def render_message_form():
    if st.session_state.form_status == "success":
        st.success(T["form_success"])
    elif st.session_state.form_status == "error":
        st.error(T["form_error"])
    elif st.session_state.form_status == "api_error":
        st.error(T["api_error"])

    with st.form("contact_form", clear_on_submit=False):
        st.text_input(T["form_name"], key="input_name")
        st.text_input(T["form_email"], key="input_email")
        st.text_area(T["form_message"], key="input_message", height=150)
        submitted = st.form_submit_button(T["form_submit"])

    if submitted:
        handle_form_submit()
        st.rerun()


def render_message_list():
    st.markdown("---")
    st.markdown("### 💬 " + T["guestbook_recent"])
    messages = api_get_messages(limit=50)
    if not messages:
        st.info(T["guestbook_empty"])
        return
    for m in reversed(messages):
        name = str(m.get("name") or "Anonymous").replace("<", "&lt;")
        body = str(m.get("message") or "").replace("<", "&lt;")
        time_str = m.get("created_at", "") or m.get("time", "")
        st.markdown(
            '<div class="msg-card">'
            '<span class="msg-name">' + name + '</span>'
            '<span class="msg-time">' + str(time_str) + '</span>'
            '<div class="msg-body">' + body + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )


# ==================== 產品頁 ====================
if page == T["nav_products"]:
    st.markdown("## " + T["products_title"])
    st.markdown("*" + T["products_desc"] + "*")
    st.markdown("---")

    if st.session_state.category == "children":
        products = [p for p in T["products"] if p[5] == "children"]
        st.markdown("### " + T["cat_children"])
    elif st.session_state.category == "adult":
        products = [p for p in T["products"] if p[5] == "adult"]
        st.markdown("### " + T["cat_adult"])
    else:
        products = T["products"]

    if not products:
        st.info("No products in this category yet.")
    else:
        cols = st.columns(2)
        for i, (key, name, desc, price, emoji, _cat) in enumerate(products):
            with cols[i % 2]:
                st.markdown("### " + emoji + " " + name)
                img_b64, mime = img_to_b64(
                    os.path.join(IMAGE_DIR, PRODUCT_IMAGES[key]), max_side=800
                )
                if img_b64:
                    st.markdown(
                        '<img src="data:' + mime + ';base64,' + img_b64 + '" '
                        'style="width:100%;border-radius:10px;" />',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<div style="background:linear-gradient(135deg,#f5f7fa,#e4e8ec);'
                        'border-radius:10px;padding:3rem;text-align:center;'
                        'border:2px dashed #ccc;color:#aaa;">'
                        '<div style="font-size:3rem;">' + emoji + '</div>'
                        '<p>' + T["no_photo"] + '</p>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    '<div class="product-card">'
                    '<p class="desc">' + desc + '</p>'
                    '<p class="price">' + price + '</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )

    with st.expander("📁 " + T["photo_hint"]):
        st.code("\n".join(["images/" + v for v in PRODUCT_IMAGES.values()]))


# ==================== 關於我們 ====================
elif page == T["nav_about"]:
    st.markdown("## " + T["about_title"])
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(T["about_text"])
    with col2:
        st.markdown(
            '<div class="contact-card">'
            '<h3>📬 Contact</h3>'
            '<p><strong>He YA</strong></p>'
            '<p><a href="mailto:hejingling51@gmail.com">hejingling51@gmail.com</a></p>'
            '<p style="margin-top:1rem;font-size:0.85rem;opacity:0.8;">'
            'Gabriel-JL Co., Ltd.<br>Socks Manufacturer & Exporter'
            '</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🏭 " + T["advantages_title"])
    adv_cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(T["advantages"]):
        with adv_cols[i]:
            st.markdown("### " + icon + " " + title)
            st.caption(desc)


# ==================== 聯絡我們 / 留言 ====================
elif page == T["nav_contact"]:
    st.markdown("## " + T["contact_title"])
    st.markdown("*" + T["contact_desc"] + "*")
    st.markdown("---")
    render_message_form()
    render_message_list()


# ==================== 頁尾 ====================
st.markdown(
    '<div style="text-align:center;padding:2rem 0 1rem 0;color:#888;'
    'font-size:0.85rem;border-top:1px solid #eee;margin-top:3rem;">'
    + T["footer"] +
    '</div>',
    unsafe_allow_html=True,
)