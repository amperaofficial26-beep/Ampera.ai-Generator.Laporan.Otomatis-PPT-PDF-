"""
Modul login sederhana, limit ekspor, watermark, pembayaran manual, dan profil branding.

CATATAN PENTING (baca sebelum pakai di production):
- SEMUA state di modul ini (jatah ekspor, status premium, profil branding, riwayat laporan)
  disimpan di st.session_state -- artinya RESET setiap kali browser/session baru/refresh
  total. Ini keterbatasan yang wajar untuk MVP tanpa database. Kalau nanti butuh data yang
  bertahan lintas sesi/perangkat (misal riwayat laporan beneran, profil klien permanen),
  itu saatnya tambah database (Supabase/Firebase/Postgres).
- Kode akses "UNLIMITED-xxx" (prefix khusus) memberi status berlangganan unlimited untuk
  SESI itu saja -- bukan langganan bulanan sungguhan (itu perlu payment gateway recurring).
"""
import streamlit as st

FREE_EXPORT_LIMIT = 8          # dinaikkan dari 3 -> 8 biar versi gratis lebih menarik dicoba
EXPORTS_PER_TOPUP = 5
MAX_BRANDING_PROFILES = 10


def check_login(username: str, password: str) -> bool:
    users = st.secrets.get("users", {})
    return username in users and users[username] == password


def login_gate():
    if st.session_state.get("logged_in"):
        return True

    with st.form("login_form"):
        st.markdown(
            '<div style="text-align:center; margin-bottom:1.2rem;">'
            '<div class="neon-title" style="font-size:1.8rem;">Ampera.AI</div>'
            '<div style="color:#9ca3af; font-size:0.85rem;">Masuk untuk melanjutkan ke Generator Laporan Otomatis</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Masuk")

    if submitted:
        with st.spinner("Memverifikasi akun..."):
            import time
            time.sleep(0.6)  # jeda kecil murni biar animasi loading kelihatan, bukan simulasi proses berat
            valid = check_login(username, password)
        if valid:
            st.session_state["logged_in"] = True
            st.session_state["show_login_transition"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Username atau password salah.")
    return False


def get_export_count() -> int:
    return st.session_state.get("export_count", 0)


def get_bonus_exports() -> int:
    return st.session_state.get("bonus_exports", 0)


def is_unlimited() -> bool:
    return st.session_state.get("unlimited_access", False)


def is_premium() -> bool:
    """Premium = pernah redeem kode apapun (topup biasa ATAU unlimited)."""
    return get_bonus_exports() > 0 or is_unlimited()


def can_export() -> bool:
    if is_unlimited():
        return True
    return get_export_count() < (FREE_EXPORT_LIMIT + get_bonus_exports())


def record_export():
    st.session_state["export_count"] = get_export_count() + 1


def remaining_free_exports():
    if is_unlimited():
        return "∞"
    total_limit = FREE_EXPORT_LIMIT + get_bonus_exports()
    return max(0, total_limit - get_export_count())


def should_show_watermark() -> bool:
    """Watermark 'dibuat dengan app ini' muncul kalau user BUKAN premium."""
    return not is_premium()


def get_payment_info() -> dict:
    return dict(st.secrets.get("payment", {}))


def redeem_access_code(code: str) -> tuple:
    """
    Cek kode akses. Kode berawalan 'UNLIMITED-' memberi status unlimited untuk sesi ini,
    kode biasa nambah bonus_exports seperti biasa.
    Return: (berhasil: bool, pesan: str)
    """
    code = code.strip()
    if not code:
        return False, "Masukkan kode akses terlebih dahulu."

    payment_info = get_payment_info()
    valid_codes = payment_info.get("access_codes", [])
    unlimited_codes = payment_info.get("unlimited_codes", [])

    used_codes = st.session_state.setdefault("used_access_codes", set())

    if code in used_codes:
        return False, "Kode ini sudah pernah dipakai di sesi ini."

    if code in unlimited_codes:
        used_codes.add(code)
        st.session_state["unlimited_access"] = True
        return True, "Kode berhasil ditukar! Kamu sekarang punya akses unlimited + semua fitur premium untuk sesi ini."

    if code in valid_codes:
        used_codes.add(code)
        st.session_state["bonus_exports"] = get_bonus_exports() + EXPORTS_PER_TOPUP
        return True, f"Kode berhasil ditukar! Kamu dapat tambahan {EXPORTS_PER_TOPUP}x jatah ekspor + akses fitur premium."

    return False, "Kode akses tidak valid. Pastikan kamu sudah menyalin persis dari admin."


# ---------- Profil Branding (multi-klien, session-based) ----------

def get_branding_profiles() -> dict:
    """Return dict {nama_profil: {title, brand_color, template, logo_bytes}}."""
    return st.session_state.setdefault("branding_profiles", {})


def save_branding_profile(name: str, brand_color: str, template: str, logo_bytes) -> tuple:
    name = name.strip()
    if not name:
        return False, "Nama profil tidak boleh kosong."
    profiles = get_branding_profiles()
    if name not in profiles and len(profiles) >= MAX_BRANDING_PROFILES:
        return False, f"Maksimal {MAX_BRANDING_PROFILES} profil per sesi."
    profiles[name] = {"brand_color": brand_color, "template": template, "logo_bytes": logo_bytes}
    return True, f"Profil '{name}' tersimpan."


def delete_branding_profile(name: str):
    profiles = get_branding_profiles()
    profiles.pop(name, None)


# ---------- Riwayat Laporan (session-based) ----------

def get_report_history() -> list:
    return st.session_state.setdefault("report_history", [])


def add_report_history(title: str, period: str, file_type: str):
    import datetime
    history = get_report_history()
    history.insert(0, {
        "title": title, "period": period, "file_type": file_type,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    st.session_state["report_history"] = history[:20]  # simpan maks 20 terakhir
