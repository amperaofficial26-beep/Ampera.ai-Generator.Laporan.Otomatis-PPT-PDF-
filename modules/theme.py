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

/* ================= 9. Kartu profil sidebar ================= */
@keyframes avatarPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.45); }
    50%      { box-shadow: 0 0 0 8px rgba(168, 85, 247, 0); }
}
.profile-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(168,85,247,0.15), rgba(77,216,255,0.08));
    border: 1px solid rgba(168, 85, 247, 0.3);
    margin-bottom: 0.7rem;
}
.profile-avatar {
    width: 42px;
    height: 42px;
    min-width: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a855f7, #4dd8ff);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 800;
    font-size: 1.1rem;
    animation: avatarPulse 2.5s infinite;
}
.profile-info .profile-name {
    font-weight: 700;
    color: #f3f4f6;
    font-size: 0.95rem;
    line-height: 1.2;
}
.profile-info .profile-role {
    font-size: 0.72rem;
    color: #9ca3af;
}
.version-badge {
    display: inline-block;
    margin-top: 3px;
    padding: 1px 8px;
    font-size: 0.65rem;
    font-weight: 700;
    border-radius: 999px;
    background: rgba(77, 216, 255, 0.15);
    color: #4dd8ff;
    border: 1px solid rgba(77, 216, 255, 0.35);
}

/* ================= 10. Kartu promosi premium sidebar ================= */
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
.premium-promo-card {
    position: relative;
    padding: 14px 16px;
    border-radius: 14px;
    background: linear-gradient(135deg, #241a3d 0%, #1a1030 100%);
    border: 1px solid rgba(250, 204, 21, 0.4);
    margin-bottom: 0.8rem;
    overflow: hidden;
}
.premium-promo-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(120deg, transparent 30%, rgba(250,204,21,0.12) 50%, transparent 70%);
    background-size: 200% 100%;
    animation: shimmer 3.5s infinite;
}
.premium-promo-card .promo-title {
    font-weight: 800;
    color: #facc15;
    font-size: 0.9rem;
    margin-bottom: 6px;
    position: relative;
}
.premium-promo-card ul {
    margin: 0;
    padding-left: 18px;
    position: relative;
}
.premium-promo-card li {
    font-size: 0.75rem;
    color: #d1d5db;
    margin-bottom: 2px;
}

/* ================= 11. Kartu fitur premium (locked / active) ================= */
.premium-locked-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(250,204,21,0.05), rgba(168,85,247,0.05));
    border: 1.5px dashed rgba(250, 204, 21, 0.4);
    margin: 0.6rem 0;
}
.premium-locked-card .lock-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #facc15;
    background: rgba(250, 204, 21, 0.12);
    border: 1px solid rgba(250, 204, 21, 0.35);
    padding: 2px 10px;
    border-radius: 999px;
    margin-bottom: 8px;
}
.premium-locked-card .locked-desc {
    color: #d1d5db;
    font-size: 0.85rem;
}

.premium-active-card {
    padding: 16px 18px;
    border-radius: 14px;
    background: linear-gradient(135deg, rgba(250,204,21,0.10), rgba(168,85,247,0.10));
    border: 1.5px solid rgba(250, 204, 21, 0.55);
    box-shadow: 0 0 20px rgba(250, 204, 21, 0.12);
    margin: 0.6rem 0 1rem 0;
}
.premium-active-card .active-badge {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #0b0d17;
    background: linear-gradient(90deg, #facc15, #fde68a);
    padding: 2px 10px;
    border-radius: 999px;
    margin-bottom: 8px;
}

/* ================= 12. Stepper modern ================= */
.modern-stepper {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin: 0.6rem 0 1.2rem 0;
    position: relative;
}
.modern-stepper::before {
    content: "";
    position: absolute;
    top: 15px;
    left: 5%;
    right: 5%;
    height: 2px;
    background: rgba(255,255,255,0.1);
    z-index: 0;
}
.stepper-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
    z-index: 1;
}
.stepper-circle {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 6px;
    border: 2px solid rgba(255,255,255,0.15);
    background: #14172a;
    color: #6b7280;
}
.stepper-circle.completed {
    background: linear-gradient(135deg, #a855f7, #4dd8ff);
    border-color: transparent;
    color: white;
    box-shadow: 0 0 12px rgba(168, 85, 247, 0.5);
}
.stepper-circle.active {
    border-color: #4dd8ff;
    color: #4dd8ff;
    box-shadow: 0 0 10px rgba(77, 216, 255, 0.5);
    animation: avatarPulse 2s infinite;
}
.stepper-label {
    font-size: 0.68rem;
    text-align: center;
    color: #9ca3af;
}
.stepper-label.active-label {
    color: #e5e7eb;
    font-weight: 700;
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


APP_VERSION = "v2.0"


def render_profile_card(username: str, role: str = "Pengguna"):
    """
    Kartu profil sidebar: avatar bulat berisi inisial nama (bukan foto asli -- upload foto
    profil sungguhan butuh fitur tambahan yang belum ada), nama, role, dan badge versi app.
    """
    initial = (username or "?").strip()[0].upper()
    st.sidebar.markdown(
        f"""
        <div class="profile-card">
            <div class="profile-avatar">{initial}</div>
            <div class="profile-info">
                <div class="profile-name">{username}</div>
                <div class="profile-role">{role}</div>
                <div class="version-badge">{APP_VERSION}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_premium_promo_card():
    """Kartu promosi upsell ke premium di sidebar, ditampilkan untuk user yang belum premium."""
    st.sidebar.markdown(
        """
        <div class="premium-promo-card">
            <div class="promo-title">✨ Upgrade ke Premium</div>
            <ul>
                <li>Proyeksi tren 30 hari</li>
                <li>Deteksi anomali otomatis</li>
                <li>Export ke Excel</li>
                <li>Google Sheets sync</li>
                <li>Profil branding tanpa batas</li>
                <li>Hapus watermark</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_premium_locked_card(description: str):
    """Kartu elegan untuk fitur premium yang masih terkunci (dashed gold border)."""
    st.markdown(
        f"""
        <div class="premium-locked-card">
            <span class="lock-badge">🔒 Fitur Premium</span>
            <div class="locked-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_premium_active_header(title: str):
    """Header elegan (gold solid border + glow) untuk section fitur premium yang sudah aktif."""
    st.markdown(
        f"""
        <div class="premium-active-card">
            <span class="active-badge">⭐ Premium Aktif</span>
            <div style="font-weight:700; color:#f3f4f6; font-size:1.05rem; margin-top:4px;">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_modern_stepper(steps: list, current_index: int):
    """Stepper horizontal modern (gradient circle, connecting line) sebagai pengganti versi teks polos."""
    parts = ['<div class="modern-stepper">']
    for i, label in enumerate(steps):
        if i < current_index:
            circle_class, content, label_class = "completed", "✓", ""
        elif i == current_index:
            circle_class, content, label_class = "active", str(i + 1), "active-label"
        else:
            circle_class, content, label_class = "", str(i + 1), ""
        parts.append(
            f'<div class="stepper-step">'
            f'<div class="stepper-circle {circle_class}">{content}</div>'
            f'<div class="stepper-label {label_class}">{label}</div>'
            f'</div>'
        )
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)
