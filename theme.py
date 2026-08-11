"""
Modul tema visual: inject CSS custom untuk tampilan dark/neon modern.

CATATAN: CSS ini menyasar elemen Streamlit lewat atribut `data-testid` (relatif stabil
lintas versi) dan tag HTML umum. Kalau Streamlit merilis versi baru yang mengubah struktur
DOM internalnya, beberapa efek bisa saja perlu disesuaikan ulang -- ini keterbatasan wajar
dari pendekatan CSS-injection (bukan fitur resmi Streamlit).
"""
import streamlit as st

CUSTOM_CSS = """
<style>
/* ================= Base dark background ================= */
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background: radial-gradient(ellipse at top, #141726 0%, #0b0d17 60%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14172a 0%, #0b0d17 100%);
    border-right: 1px solid rgba(168, 85, 247, 0.25);
}

/* ================= 1. Judul neon warna-warni ================= */
@keyframes neonShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.neon-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #ff4dd8, #a855f7, #4dd8ff, #4dff88, #ff4dd8);
    background-size: 300% auto;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: neonShift 6s ease-in-out infinite;
    text-shadow: 0 0 18px rgba(168, 85, 247, 0.35);
    margin-bottom: 0.2rem;
}

/* ================= 2. Logo sidebar naik-turun ================= */
@keyframes floatUpDown {
    0%   { transform: translateY(0px); }
    50%  { transform: translateY(-8px); }
    100% { transform: translateY(0px); }
}
.sidebar-floating-logo {
    text-align: center;
    font-size: 3rem;
    animation: floatUpDown 3.5s ease-in-out infinite;
    filter: drop-shadow(0 0 12px rgba(168, 85, 247, 0.6));
    margin-bottom: 0.5rem;
}

/* ================= 3. Kotak jatah ekspor - border neon ================= */
@keyframes borderGlow {
    0%   { box-shadow: 0 0 8px 1px #ff4dd8, inset 0 0 6px rgba(255,77,216,0.15); border-color: #ff4dd8; }
    33%  { box-shadow: 0 0 8px 1px #a855f7, inset 0 0 6px rgba(168,85,247,0.15); border-color: #a855f7; }
    66%  { box-shadow: 0 0 8px 1px #4dd8ff, inset 0 0 6px rgba(77,216,255,0.15); border-color: #4dd8ff; }
    100% { box-shadow: 0 0 8px 1px #ff4dd8, inset 0 0 6px rgba(255,77,216,0.15); border-color: #ff4dd8; }
}
.neon-quota-box {
    border: 2px solid #a855f7;
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
    background: rgba(20, 23, 42, 0.6);
    animation: borderGlow 4s linear infinite;
    margin-bottom: 0.8rem;
}
.neon-quota-box .quota-label {
    font-size: 0.75rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.neon-quota-box .quota-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #f5f5f5;
    text-shadow: 0 0 10px rgba(168, 85, 247, 0.6);
}

/* ================= 4. Tulisan muncul perlahan (fade-in) ================= */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
[data-testid="stMarkdownContainer"], h1, h2, h3, p, label {
    animation: fadeInUp 0.6s ease-out;
}

/* ================= 6. Kartu login di tengah ================= */
[data-testid="stForm"] {
    max-width: 420px;
    margin: 8vh auto;
    padding: 2.2rem 2rem;
    border-radius: 18px;
    background: rgba(20, 23, 42, 0.75);
    border: 1px solid rgba(168, 85, 247, 0.35);
    box-shadow: 0 0 30px rgba(168, 85, 247, 0.25), 0 0 60px rgba(77, 216, 255, 0.08);
    backdrop-filter: blur(6px);
    animation: fadeInUp 0.7s ease-out;
}

/* Loading spinner custom */
[data-testid="stSpinner"] div {
    border-top-color: #a855f7 !important;
    border-right-color: #4dd8ff !important;
}

/* ================= 7. Transisi dramatis (curtain split) ================= */
@keyframes splitLeft {
    from { transform: translateX(0); }
    to   { transform: translateX(-100%); }
}
@keyframes splitRight {
    from { transform: translateX(0); }
    to   { transform: translateX(100%); }
}
.curtain-left, .curtain-right {
    position: fixed;
    top: 0;
    width: 50vw;
    height: 100vh;
    background: linear-gradient(135deg, #a855f7, #0b0d17);
    z-index: 999999;
    pointer-events: none;
}
.curtain-left {
    left: 0;
    animation: splitLeft 1.1s cubic-bezier(0.83, 0, 0.17, 1) 0.15s forwards;
}
.curtain-right {
    right: 0;
    animation: splitRight 1.1s cubic-bezier(0.83, 0, 0.17, 1) 0.15s forwards;
}

/* ================= 8. Tombol menimbul + glow saat hover ================= */
.stButton > button, .stDownloadButton > button, [data-testid="stLinkButton"] a {
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
    border: 1px solid rgba(168, 85, 247, 0.4) !important;
}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stLinkButton"] a:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 6px 20px rgba(168, 85, 247, 0.45), 0 0 12px rgba(77, 216, 255, 0.35);
    border-color: #4dd8ff !important;
}
</style>
"""


def inject_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_animated_title(text: str):
    st.markdown(f'<div class="neon-title">{text}</div>', unsafe_allow_html=True)


def render_sidebar_logo(emoji: str = "📊"):
    st.sidebar.markdown(f'<div class="sidebar-floating-logo">{emoji}</div>', unsafe_allow_html=True)


def render_export_quota_box(value_display, label: str = "Jatah Ekspor Tersisa"):
    st.sidebar.markdown(
        f"""
        <div class="neon-quota-box">
            <div class="quota-label">{label}</div>
            <div class="quota-value">{value_display}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_transition():
    """
    Panggil SEKALI tepat setelah login berhasil (pakai flag session_state supaya
    cuma muncul sekali, bukan tiap rerun). Overlay ini otomatis menghilang sendiri
    lewat animasi CSS (translateX keluar layar) tanpa perlu JS/timer manual.
    """
    st.markdown(
        '<div class="curtain-left"></div><div class="curtain-right"></div>',
        unsafe_allow_html=True,
    )
