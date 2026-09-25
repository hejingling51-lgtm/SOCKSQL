# SOCKSW.py
import streamlit as st
import os
import io
import base64
import requests
from PIL import Image, ImageFilter, ImageDraw

# ==================== API 設定 ====================
API_BASE = os.environ.get("API_BASE", "https://socksql.onrender.com")


# ==================== API 工具函式 ====================
def api_get_messages(limit=50):
    try:
        r = requests.get(f"{API_BASE}/api/messages",
                         params={"limit": limit}, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"讀取留言失敗：{e}")
        return []


def api_post_message(name, email, message):
    """回傳 (ok: bool, error: str|None)。"""
    try:
        r = requests.post(
            f"{API_BASE}/api/messages",
            json={"name": name, "email": email, "message": message},
            timeout=15,
        )
        if r.status_code == 201:
            return True, None
        try:
            err = r.json().get("error", f"HTTP {r.status_code}")
        except Exception:
            err = f"HTTP {r.status_code}"
        return False, err
    except Exception as e:
        return False, str(e)


def api_get_visits():
    try:
        r = requests.get(f"{API_BASE}/api/visits", timeout=15)
        r.raise_for_status()
        return r.json().get("count", 0)
    except Exception:
        return 0


def api_inc_visits():
    try:
        r = requests.post(f"{API_BASE}/api/visits", timeout=15)
        r.raise_for_status()
        return r.json().get("count", 0)
    except Exception:
        return 0


# ==================== 頁面配置 ====================
st.set_page_config(
    page_title="Gabriel-JL Co., Ltd. | SOCKS",
    page_icon="🧦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== 路徑設定 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = BASE_DIR

PRODUCT_IMAGES = {f"product{i}": f"product{i}.jpg" for i in range(1, 11)}
DUCK_IMAGE = "duck.jpg"


# ==================== 備援：用 PIL 畫一隻鴨子 ====================
def _draw_fallback_duck(size=200):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 200.0
    d.ellipse([40*s, 90*s, 160*s, 170*s], fill=(0, 0, 0, 255))
    d.ellipse([120*s, 40*s, 180*s, 100*s], fill=(0, 0, 0, 255))
    d.polygon([(120*s, 70*s), (140*s, 70*s),
               (150*s, 120*s), (120*s, 120*s)], fill=(0, 0, 0, 255))
    d.polygon([(178*s, 68*s), (200*s, 78*s), (178*s, 88*s)], fill=(0, 0, 0, 255))
    d.polygon([(40*s, 110*s), (10*s, 90*s), (40*s, 140*s)], fill=(0, 0, 0, 255))
    d.ellipse([155*s, 60*s, 165*s, 70*s], fill=(255, 255, 255, 255))
    d.rectangle([70*s, 165*s, 80*s, 195*s], fill=(0, 0, 0, 255))
    d.rectangle([110*s, 165*s, 120*s, 195*s], fill=(0, 0, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@st.cache_data(show_spinner=False)
def _make_duck_from_file(image_path, rotate_degrees=90, crop_border=8,
                         line_threshold=40, line_color=(0, 0, 0),
                         thicken=True, thicken_passes=2):
    img = Image.open(image_path).convert("RGB")
    if rotate_degrees == 90:
        img = img.transpose(Image.ROTATE_90)
    elif rotate_degrees == 180:
        img = img.transpose(Image.ROTATE_180)
    elif rotate_degrees == 270:
        img = img.transpose(Image.ROTATE_270)
    if crop_border > 0:
        w, h = img.size
        img = img.crop((crop_border, crop_border, w - crop_border, h - crop_border))
    img = img.convert("RGBA")
    new_data = []
    for r, g, b, a in img.getdata():
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        if brightness <= line_threshold:
            new_data.append((line_color[0], line_color[1], line_color[2], 255))
        else:
            new_data.append((0, 0, 0, 0))
    img.putdata(new_data)
    if thicken and thicken_passes > 0:
        alpha = img.split()[3]
        for _ in range(thicken_passes):
            alpha = alpha.filter(ImageFilter.MaxFilter(3))
        r, g, b, _ = img.split()
        img = Image.merge("RGBA", (r, g, b, alpha))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def make_duck_clean(image_path, **kwargs):
    if not os.path.exists(image_path):
        return _draw_fallback_duck()
    try:
        return _make_duck_from_file(image_path, **kwargs)
    except Exception as e:
        print("Duck image error:", e)
        return _draw_fallback_duck()


@st.cache_data(show_spinner=False)
def load_image_b64(filename):
    path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            raw = f.read()
        img = Image.open(io.BytesIO(raw))
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        max_side = 1200
        if max(img.size) > max_side:
            ratio = max_side / max(img.size)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                             Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print("Image load error:", path, e)
        return None


# ==================== 載入鴨子圖 ====================
duck_path = os.path.join(IMAGE_DIR, DUCK_IMAGE)
duck_b64 = make_duck_clean(duck_path, rotate_degrees=90, crop_border=8,
                           line_threshold=40, line_color=(0, 0, 0),
                           thicken=True, thicken_passes=2)
duck_src = "data:image/png;base64," + duck_b64
ducks_html = (
    '<img src="' + duck_src + '" class="duck-img duck-big" alt="big duck">'
    '<img src="' + duck_src + '" class="duck-img duck-medium" alt="medium duck">'
    '<img src="' + duck_src + '" class="duck-img duck-small" alt="small duck">'
)


# ==================== 瀏覽計次（改用 API，加 30 秒快取） ====================
@st.cache_data(ttl=30, show_spinner=False)
def _cached_get_visits():
    return api_get_visits()


if "visited" not in st.session_state:
    st.session_state.visited = True
    visit_count = api_inc_visits()
else:
    visit_count = _cached_get_visits()


# ==================== 自訂 CSS ====================
CSS = """
<style>
    * { font-family: 'Helvetica Neue', 'Microsoft YaHei', sans-serif; }
    .header-banner {
        position: relative;
        background: linear-gradient(135deg, #a8b8e8 0%, #b8a8e0 50%, #9fa8e0 100%);
        padding: 1.5rem 2rem; border-radius: 12px; text-align: center;
        margin-bottom: 1.5rem; box-shadow: 0 4px 16px rgba(168, 184, 232, 0.4);
        overflow: hidden; min-height: 170px;
    }
    .header-banner .duck-img {
        position: absolute; pointer-events: none; width: auto;
        background: transparent; border: none; outline: none; box-shadow: none;
    }
    .header-banner .duck-big {
        height: 90px; top: 25px; right: 300px;
        animation: duckWalk 3.0s ease-in-out infinite; animation-delay: 0s; z-index: 10;
    }
    .header-banner .duck-medium {
        height: 55px; top: 55px; right: 210px;
        animation: duckWalk 3.0s ease-in-out infinite; animation-delay: 0.5s; z-index: 8;
    }
    .header-banner .duck-small {
        height: 32px; top: 80px; right: 140px;
        animation: duckWalk 3.0s ease-in-out infinite; animation-delay: 1.0s; z-index: 6;
    }
    @keyframes duckWalk {
        0%   { transform: translateX(0); }
        10%  { transform: translateX(10px); }
        20%  { transform: translateX(20px); }
        30%  { transform: translateX(30px); }
        40%  { transform: translateX(40px); }
        50%  { transform: translateX(50px); }
        60%  { transform: translateX(40px); }
        70%  { transform: translateX(30px); }
        80%  { transform: translateX(20px); }
        90%  { transform: translateX(10px); }
        100% { transform: translateX(0); }
    }
    .header-banner h1 {
        color: #ffffff; font-size: 1.8rem; margin: 0;
        letter-spacing: 1.5px; position: relative; z-index: 20;
        padding-right: 400px; text-align: left;
    }
    .header-banner p {
        color: #ffffff; font-size: 1rem; margin-top: 0.3rem;
        font-weight: 300; position: relative; z-index: 20;
        padding-right: 400px; text-align: left;
    }
    .visit-counter {
        display: inline-flex; align-items: center; gap: 0.6rem;
        background: rgba(255,255,255,0.85); border: 2px solid #1a1a1a;
        border-radius: 40px; padding: 0.4rem 1.2rem;
        font-family: monospace; font-size: 1rem;
        color: #1a1a1a; margin-bottom: 1rem;
    }
    .visit-counter .num { font-weight: 700; font-size: 1.4rem; color: #000; }
    .product-card {
        background: #ffffff; border-radius: 12px; padding: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem; border: 1px solid #f0f0f0;
    }
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    .product-card .price { color: #e94560; font-size: 1.3rem; font-weight: bold; }
    .product-card .desc { color: #555; font-size: 0.95rem; line-height: 1.6; }
    .contact-card {
        background: linear-gradient(135deg, #0f3460, #16213e);
        color: #fff; border-radius: 12px; padding: 2rem; text-align: center;
    }
    .contact-card a { color: #e94560; text-decoration: none; }
    .footer {
        text-align: center; padding: 2rem 0 1rem 0;
        color: #888; font-size: 0.85rem;
        border-top: 1px solid #eee; margin-top: 3rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
        "about_text": """
**Gabriel-JL Co., Ltd.** (Contact: He YA) is a professional manufacturer and exporter of all kinds of socks.

We specialize in:
- 🏃 Sports socks (running, basketball, cycling)
- 👔 Business & dress socks
- 🧦 Casual & fashion socks
- 🏭 Custom OEM/ODM orders
- 🌿 Organic cotton & bamboo fiber socks

With years of experience in the textile industry, we are committed to providing premium quality products with competitive prices.

**Email:** hejingling51@gmail.com
""",
        "contact_title": "Send Us a Message",
        "contact_desc": "We'd love to hear from you! Leave your message below and we'll get back to you within 24 hours.",
        "form_name": "Your Name",
        "form_email": "Your Email",
        "form_message": "Your Message",
        "form_submit": "Send Message",
        "form_success": "✅ Thank you! Your message has been received. We'll contact you soon.",
        "form_error": "⚠️ Please fill in all fields.",
        "product1_name": "Sports Socks",
        "product1_desc": "Breathable, moisture-wicking, cushioned sole. Perfect for running and outdoor activities.",
        "product1_price": "$2.50 - $4.00 / pair",
        "product2_name": "Business Socks",
        "product2_desc": "Elegant design, premium cotton blend. Comfortable for all-day office wear.",
        "product2_price": "$3.00 - $5.00 / pair",
        "product3_name": "Casual Socks",
        "product3_desc": "Soft, colorful, and stylish. Great for everyday wear and gifts.",
        "product3_price": "$1.80 - $3.00 / pair",
        "product4_name": "Custom OEM Socks",
        "product4_desc": "Your logo, your design, your colors. MOQ from 500 pairs. Free sample available.",
        "product4_price": "Negotiable",
        "product5_name": "Ankle Socks",
        "product5_desc": "Low-cut, invisible design. Perfect for sneakers and casual shoes.",
        "product5_price": "$1.50 - $2.60 / pair",
        "product6_name": "Kids Socks",
        "product6_desc": "Soft and safe for children. Various cute designs available.",
        "product6_price": "$1.50 - $2.50 / pair",
        "product7_name": "Baby Socks",
        "product7_desc": "Ultra-soft cotton for newborns. Anti-slip sole and gentle elastic band.",
        "product7_price": "$1.20 - $2.00 / pair",
        "product8_name": "School Socks",
        "product8_desc": "Durable knee-high socks for school uniforms. Easy to wash and keep white.",
        "product8_price": "$1.60 - $2.80 / pair",
        "product9_name": "Toddler Socks",
        "product9_desc": "Fun cartoon patterns for toddlers. Non-slip grip and breathable fabric.",
        "product9_price": "$1.30 - $2.20 / pair",
        "product10_name": "Teen Sports Socks",
        "product10_desc": "Athletic socks for teenagers. Cushioned, durable, and colorful.",
        "product10_price": "$2.00 - $3.50 / pair",
        "footer": "© 2025 Gabriel-JL Co., Ltd. All rights reserved. | Contact: He YA | hejingling51@gmail.com",
        "lang_switch": "🇨🇳 中文",
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
        "message_log": "📝 Message Log",
        "no_messages": "No messages yet. Be the first to leave one!",
        "api_error": "⚠️ API connection failed. Please try again later.",
        "err_invalid_email": "⚠️ Invalid email format.",
        "err_too_long": "⚠️ Input too long.",
        "err_missing_fields": "⚠️ Please fill in all fields.",
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
        "about_text": """
**Gabriel-JL 有限公司**（聯絡人：He YA）是一家專業的襪子製造商和出口商。

我們專注於：
- 🏃 運動襪（跑步、籃球、騎行）
- 👔 商務正裝襪
- 🧦 休閒時尚襪
- 🏭 訂製 OEM/ODM 訂單
- 🌿 有機棉與竹纖維襪

憑藉多年的紡織行業經驗，我們致力於以有競爭力的價格提供優質產品。

**郵箱：** hejingling51@gmail.com
""",
        "contact_title": "給我們留言",
        "contact_desc": "歡迎聯絡我們！請在下方留言，我們會在24小時內回覆您。",
        "form_name": "您的姓名",
        "form_email": "您的郵箱",
        "form_message": "您的留言",
        "form_submit": "發送留言",
        "form_success": "✅ 感謝您！我們已收到您的留言，會盡快與您聯絡。",
        "form_error": "⚠️ 請填寫所有欄位。",
        "product1_name": "運動襪",
        "product1_desc": "透氣吸汗，加厚緩衝鞋底。適合跑步、健身及戶外運動。",
        "product1_price": "$2.50 - $4.00 / 雙",
        "product2_name": "商務襪",
        "product2_desc": "優雅設計，優質棉混紡。適合全天辦公穿著，舒適有型。",
        "product2_price": "$3.00 - $5.00 / 雙",
        "product3_name": "休閒襪",
        "product3_desc": "柔軟多彩，時尚百搭。適合日常穿著和送禮。",
        "product3_price": "$1.80 - $3.00 / 雙",
        "product4_name": "訂製 OEM 襪子",
        "product4_desc": "您的Logo、您的設計、您的顏色。起訂量500雙起，可提供免費樣品。",
        "product4_price": "面議",
        "product5_name": "船襪 / 隱形襪",
        "product5_desc": "低筒隱形設計。完美搭配運動鞋與休閒鞋。",
        "product5_price": "$1.50 - $2.60 / 雙",
        "product6_name": "兒童襪",
        "product6_desc": "柔軟安全，適合兒童。多款可愛設計可選。",
        "product6_price": "$1.50 - $2.50 / 雙",
        "product7_name": "嬰兒襪",
        "product7_desc": "超柔軟純棉，適合新生兒。防滑鞋底與溫和鬆緊帶。",
        "product7_price": "$1.20 - $2.00 / 雙",
        "product8_name": "學生襪",
        "product8_desc": "耐穿及膝襪，適合校服。易洗滌、常保潔白。",
        "product8_price": "$1.60 - $2.80 / 雙",
        "product9_name": "幼兒襪",
        "product9_desc": "趣味卡通圖案，適合幼兒。防滑設計、透氣材質。",
        "product9_price": "$1.30 - $2.20 / 雙",
        "product10_name": "青少年運動襪",
        "product10_desc": "適合青少年的運動襪。加厚耐穿、色彩活潑。",
        "product10_price": "$2.00 - $3.50 / 雙",
        "footer": "© 2025 Gabriel-JL 有限公司 版權所有 | 聯絡人: He YA | hejingling51@gmail.com",
        "lang_switch": "🇬🇧 English",
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
        "message_log": "📝 留言紀錄",
        "no_messages": "目前沒有留言，歡迎成為第一個留言的人！",
        "api_error": "⚠️ API 連線失敗，請稍後再試。",
        "err_invalid_email": "⚠️ 電子郵件格式不正確。",
        "err_too_long": "⚠️ 輸入內容過長。",
        "err_missing_fields": "⚠️ 請填寫所有欄位。",
    },
}

PRODUCT_CATEGORY = {
    "product1": "adult", "product2": "adult", "product3": "adult",
    "product4": "adult", "product5": "adult",
    "product6": "children", "product7": "children", "product8": "children",
    "product9": "children", "product10": "children",
}


# ==================== Session State ====================
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "form_status" not in st.session_state:
    st.session_state.form_status = None
if "form_error_detail" not in st.session_state:
    st.session_state.form_error_detail = None
if "category" not in st.session_state:
    st.session_state.category = "all"
if "form_key" not in st.session_state:
    st.session_state.form_key = 0


def toggle_lang():
    st.session_state.lang = "zh" if st.session_state.lang == "en" else "en"


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
    '<span class="num">' + f"{visit_count:,}" + '</span>'
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
        cat_options = {
            "all": T["cat_all"],
            "children": T["cat_children"],
            "adult": T["cat_adult"],
        }
        cat_keys = list(cat_options.keys())
        cat_labels = list(cat_options.values())
        try:
            current_idx = cat_keys.index(st.session_state.category)
        except ValueError:
            current_idx = 0
        selected_label = st.radio(
            "Category", cat_labels, index=current_idx,
            label_visibility="collapsed", key="cat_radio",
        )
        st.session_state.category = cat_keys[cat_labels.index(selected_label)]

    st.markdown("---")
    st.markdown("**📧 Email:**  \nhejingling51@gmail.com")
    st.markdown("**👤 Contact:**  \nHe YA")
    st.markdown("---")
    st.caption("Gabriel-JL Co., Ltd.")


# ==================== 產品展示 ====================
if page == T["nav_products"]:
    st.markdown("## " + T["products_title"])
    st.markdown("*" + T["products_desc"] + "*")
    st.markdown("---")

    all_products = [
        {"key": "product1", "name": T["product1_name"], "desc": T["product1_desc"],
         "price": T["product1_price"], "emoji": "🏃"},
        {"key": "product2", "name": T["product2_name"], "desc": T["product2_desc"],
         "price": T["product2_price"], "emoji": "👔"},
        {"key": "product3", "name": T["product3_name"], "desc": T["product3_desc"],
         "
