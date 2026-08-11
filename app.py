"""
Generator Laporan Otomatis (PPT/PDF/Excel) untuk Konsultan & Agensi
Upload data (atau Google Sheets) -> insight & metric cards -> branding -> export.
"""
import streamlit as st
import pandas as pd
from datetime import date

from modules.data_parser import load_data, detect_columns, coerce_date_column, summarize_metrics
from modules.chart_generator import (
    make_trend_chart, make_bar_chart, make_trend_chart_plotly, make_bar_chart_plotly
)
from modules.ppt_generator import generate_pptx
from modules.pdf_generator import generate_pdf
from modules.excel_generator import generate_excel
from modules.insight_generator import (
    generate_all_insights, generate_metric_deltas, generate_narrative_summary,
    generate_period_insights, generate_category_insights
)
from modules.forecast_generator import forecast_metric, make_forecast_chart, generate_forecast_text
from modules.anomaly_detector import generate_anomaly_insights
from modules.preview_generator import pdf_bytes_to_images, pptx_bytes_to_images
from modules.sheets_connector import fetch_google_sheet
from modules.auth_billing import (
    login_gate, can_export, record_export, remaining_free_exports, FREE_EXPORT_LIMIT,
    get_payment_info, redeem_access_code, EXPORTS_PER_TOPUP, is_premium, is_unlimited,
    should_show_watermark, get_branding_profiles, save_branding_profile, delete_branding_profile,
    get_report_history, add_report_history,
)
from modules.theme import (
    inject_custom_css, render_animated_title, render_export_quota_box, render_page_transition,
    render_profile_card, render_premium_promo_card, render_premium_locked_card,
    render_premium_active_header, render_modern_stepper,
)

st.set_page_config(page_title="Generator Laporan Otomatis", page_icon="📊", layout="wide")
inject_custom_css()

# ---------- 0. Login (opsional) ----------
USE_LOGIN = bool(st.secrets.get("users", {}))
if USE_LOGIN:
    if not login_gate():
        st.stop()
    # Transisi dramatis: tampil SEKALI tepat setelah login berhasil (flag diset oleh login_gate)
    if st.session_state.get("show_login_transition", False):
        render_page_transition()
        st.session_state["show_login_transition"] = False

render_animated_title("📊 Generator Laporan Otomatis")
st.caption("Upload data performa (atau sambungkan Google Sheets), lihat insight otomatis, atur branding, dan ekspor jadi PPT/PDF/Excel siap presentasi.")

if USE_LOGIN:
    render_profile_card(st.session_state.get("username", "Pengguna"), role="Anggota Ampera.AI")
else:
    render_profile_card("Tamu", role="Mode tanpa login")

render_export_quota_box(remaining_free_exports())
if is_unlimited():
    st.sidebar.success("⭐ Status: Unlimited (sesi ini)")
elif is_premium():
    st.sidebar.success("⭐ Status: Premium aktif (sesi ini)")
else:
    st.sidebar.caption("Status: Gratis")
    render_premium_promo_card()

# Riwayat laporan (sidebar)
history = get_report_history()
if history:
    with st.sidebar.expander(f"🕘 Riwayat Laporan ({len(history)})"):
        for h in history[:10]:
            st.caption(f"{h['timestamp']} — {h['title']} ({h['file_type']})")
        st.caption("_Riwayat ini hanya tersimpan selama sesi browser ini berlangsung._")

# ---------- Progress stepper ----------
STEPS = ["Upload Data", "Pilih Kolom", "Branding", "Insight", "Export"]


def render_stepper(current_index: int):
    render_modern_stepper(STEPS, current_index)


current_step = 0
render_stepper_placeholder = st.empty()

# ---------- 1. Upload data (multi-file + Google Sheets) ----------
st.header("1. Upload Data")

source_mode = st.radio("Sumber data", ["Upload File", "Google Sheets (Premium)"], horizontal=True)

df = None

if source_mode == "Upload File":
    uploaded_files = st.file_uploader(
        "Upload 1 atau beberapa file CSV/Excel (Meta Ads, Google Analytics, penjualan, dll)",
        type=["csv", "xlsx", "xls"], accept_multiple_files=True,
    )

    if not uploaded_files:
        with render_stepper_placeholder.container():
            render_stepper(0)
        st.info("Silakan upload file data untuk mulai membuat laporan.")
        st.stop()

    dfs = []
    for f in uploaded_files:
        try:
            dfs.append(load_data(f))
        except Exception as e:
            st.error(f"Gagal membaca file '{f.name}': {e}")
            st.stop()

    if len(dfs) == 1:
        df = dfs[0]
    else:
        st.caption(f"{len(dfs)} file diupload — digabung otomatis (kolom yang cocok akan disatukan).")
        try:
            df = pd.concat(dfs, ignore_index=True, sort=False)
        except Exception as e:
            st.error(f"Gagal menggabungkan file: {e}")
            st.stop()

else:  # Google Sheets
    if not is_premium():
        with render_stepper_placeholder.container():
            render_stepper(0)
        render_premium_locked_card("🔗 <b>Koneksi Google Sheets</b> — sambungkan data langsung dari spreadsheet tanpa upload manual. Tukar kode akses di bagian Export, atau pakai 'Upload File' dulu.")
        st.stop()

    sheet_url = st.text_input(
        "Paste link Google Sheets (pastikan share access 'Anyone with the link')",
        placeholder="https://docs.google.com/spreadsheets/d/....../edit#gid=0",
    )
    if not sheet_url:
        with render_stepper_placeholder.container():
            render_stepper(0)
        st.info("Masukkan link Google Sheets untuk melanjutkan.")
        st.stop()

    with st.spinner("Mengambil data dari Google Sheets..."):
        df, sheet_err = fetch_google_sheet(sheet_url)
    if sheet_err:
        st.error(sheet_err)
        st.stop()

st.success(f"Data berhasil dimuat: {df.shape[0]} baris, {df.shape[1]} kolom")
with st.expander("Lihat preview data"):
    st.dataframe(df.head(20), use_container_width=True)

detected = detect_columns(df)
current_step = 1

# ---------- 2. Mapping kolom ----------
st.header("2. Pilih Kolom Data")
col1, col2 = st.columns(2)

with col1:
    date_col = st.selectbox(
        "Kolom tanggal (untuk chart tren)",
        options=["(tidak ada)"] + list(df.columns),
        index=(df.columns.get_loc(detected["suggested_date"]) + 1) if detected["suggested_date"] else 0,
    )
    metric_cols = st.multiselect(
        "Kolom metrik (numerik) yang ingin ditampilkan",
        options=detected["numeric_cols"],
        default=detected["suggested_metrics"],
    )

with col2:
    category_col = st.selectbox(
        "Kolom kategori (opsional, untuk bar chart perbandingan)",
        options=["(tidak ada)"] + detected["categorical_cols"],
    )

if not metric_cols:
    with render_stepper_placeholder.container():
        render_stepper(1)
    st.warning("Pilih minimal satu kolom metrik untuk melanjutkan.")
    st.stop()

if date_col != "(tidak ada)":
    df = coerce_date_column(df, date_col)

current_step = 2

# ---------- 3. Branding, Template & Profil ----------
st.header("3. Branding & Template")

profiles = get_branding_profiles()
profile_names = ["(Baru)"] + list(profiles.keys())
selected_profile = st.selectbox("Profil branding klien", options=profile_names)

if selected_profile != "(Baru)":
    p = profiles[selected_profile]
    default_color, default_template, default_logo = p["brand_color"], p["template"], p["logo_bytes"]
else:
    default_color, default_template, default_logo = "#2563EB", "corporate", None

b1, b2, b3 = st.columns(3)

with b1:
    report_title = st.text_input("Judul Laporan", value="Laporan Performa")
    period_label = st.text_input("Periode", value=f"Diperbarui {date.today().strftime('%d %B %Y')}")
    lang_choice = st.selectbox("Bahasa Label Laporan", options=["id", "en"],
                                format_func=lambda x: "Indonesia" if x == "id" else "English")

with b2:
    brand_color = st.color_picker("Warna Brand", value=default_color)
    template_options = ["corporate", "minimalist", "colorful"]
    template_choice = st.selectbox(
        "Gaya Template", options=template_options,
        index=template_options.index(default_template) if default_template in template_options else 0,
        format_func=lambda x: {"corporate": "Corporate (cover solid)",
                                "minimalist": "Minimalist (aksen garis)",
                                "colorful": "Colorful (aksen tebal)"}[x],
    )

with b3:
    logo_file = st.file_uploader("Upload Logo (opsional)", type=["png", "jpg", "jpeg"], key="logo")
    logo_bytes = logo_file.read() if logo_file else default_logo
    if logo_bytes:
        st.image(logo_bytes, width=120, caption="Preview logo")

with st.expander("💾 Simpan sebagai profil branding (untuk klien lain nanti)"):
    if not is_premium():
        st.caption("Multi-profil branding tak terbatas adalah fitur premium. Versi gratis: 1 profil aktif per sesi.")
    profile_name_input = st.text_input("Nama profil (misal: 'Klien ABC')", key="profile_name_input")
    save_col, del_col = st.columns(2)
    with save_col:
        if st.button("Simpan Profil", use_container_width=True):
            if not is_premium() and len(profiles) >= 1 and profile_name_input not in profiles:
                st.error("Versi gratis cuma bisa simpan 1 profil. Tukar kode akses untuk buka profil tak terbatas.")
            else:
                ok, msg = save_branding_profile(profile_name_input, brand_color, template_choice, logo_bytes)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    with del_col:
        if selected_profile != "(Baru)" and st.button(f"Hapus Profil '{selected_profile}'", use_container_width=True):
            delete_branding_profile(selected_profile)
            st.rerun()

current_step = 3

# ---------- 4. Metric cards, Insight, Anomali, Proyeksi ----------
st.header("4. Ringkasan & Insight")

deltas = generate_metric_deltas(df, date_col, metric_cols)
if deltas:
    cards = st.columns(len(deltas))
    for col, (name, stats) in zip(cards, deltas.items()):
        delta_display = f"{stats['delta_pct']:+.1f}%" if stats["delta_pct"] is not None else None
        col.metric(label=name, value=f"{stats['total']:,.0f}", delta=delta_display)

insights = generate_all_insights(
    df,
    date_col=date_col if date_col != "(tidak ada)" else None,
    metric_cols=metric_cols,
    category_col=category_col if category_col != "(tidak ada)" else None,
)

summary = summarize_metrics(df, metric_cols)

p_insights_raw = generate_period_insights(df, date_col, metric_cols) if date_col != "(tidak ada)" else []
c_insights_raw = generate_category_insights(df, category_col, metric_cols) if category_col != "(tidak ada)" else []

# Ringkasan naratif rule-based (gratis, tanpa API/AI apapun)
narrative = generate_narrative_summary(report_title, period_label, summary, p_insights_raw, c_insights_raw)
if narrative:
    st.markdown("**Ringkasan Eksekutif:**")
    st.info(narrative)

if insights:
    with st.expander("Lihat semua insight statistik"):
        for text in insights:
            st.markdown(f"- {text}")
else:
    st.caption("Belum cukup data untuk menghasilkan insight otomatis (butuh kolom tanggal/kategori & data yang cukup).")

# --- Deteksi Anomali (PREMIUM) ---
anomaly_insights = []
if not is_premium():
    render_premium_locked_card("🔍 <b>Deteksi Anomali</b> — temukan titik data yang menyimpang tidak wajar secara otomatis. Tukar kode akses untuk membuka fitur ini.")
elif date_col == "(tidak ada)":
    st.subheader("🔍 Deteksi Anomali")
    st.caption("Pilih kolom tanggal untuk mengaktifkan deteksi anomali.")
else:
    render_premium_active_header("🔍 Deteksi Anomali")
    anomaly_insights = generate_anomaly_insights(df, date_col, metric_cols)
    if anomaly_insights:
        for text in anomaly_insights:
            st.markdown(f"- ⚠️ {text}")
    else:
        st.caption("Tidak ada anomali signifikan terdeteksi pada data ini.")

# --- Proyeksi Tren (PREMIUM) ---
if not is_premium():
    render_premium_locked_card("📈 <b>Proyeksi Tren 30 Hari</b> — lihat estimasi arah metrik ke depan berdasarkan tren historis. Tukar kode akses untuk membuka fitur ini.")
elif date_col == "(tidak ada)":
    st.subheader("📈 Proyeksi Tren 30 Hari")
    st.caption("Pilih kolom tanggal untuk mengaktifkan proyeksi tren.")
else:
    render_premium_active_header("📈 Proyeksi Tren 30 Hari")
    forecast_metric_choice = st.selectbox("Pilih metrik untuk diproyeksikan", options=metric_cols, key="forecast_metric")
    forecast_result = forecast_metric(df, date_col, forecast_metric_choice, forecast_days=30)
    if forecast_result is None:
        st.caption("Data terlalu sedikit untuk membuat proyeksi (butuh minimal 5 titik data).")
    else:
        forecast_chart_png = make_forecast_chart(forecast_metric_choice, forecast_result, brand_color=brand_color)
        st.image(forecast_chart_png, use_container_width=True)
        st.markdown(generate_forecast_text(forecast_metric_choice, forecast_result))

# ---------- 5. Preview chart & Urutan Slide ----------
st.header("5. Preview Chart")

try:
    import plotly  # noqa: F401
    use_plotly = True
except ImportError:
    use_plotly = False
    st.caption("Plotly belum terinstall — menampilkan chart versi statis.")

available_chart_specs = []
if date_col != "(tidak ada)":
    for m in metric_cols:
        available_chart_specs.append(("trend", m, f"Tren {m}"))
if category_col != "(tidak ada)" and metric_cols:
    for m in metric_cols:
        available_chart_specs.append(("bar", m, f"{m} per {category_col}"))

chart_order_labels = [spec[2] for spec in available_chart_specs]
if is_premium() and len(chart_order_labels) > 1:
    st.caption("🔀 Urutan chart di laporan (fitur premium) — atur urutan tampil:")
    ordered_labels = st.multiselect(
        "Klik urut sesuai keinginan (yang belum diklik otomatis ditambah di akhir)",
        options=chart_order_labels, default=chart_order_labels,
    )
    remaining = [l for l in chart_order_labels if l not in ordered_labels]
    final_order = ordered_labels + remaining
else:
    final_order = chart_order_labels

spec_by_label = {spec[2]: spec for spec in available_chart_specs}
chart_images = []

for label in final_order:
    kind, m, title_ = spec_by_label[label]
    if kind == "trend":
        png = make_trend_chart(df, date_col, m, brand_color=brand_color, title=title_)
        chart_images.append((title_, png))
        if use_plotly:
            st.plotly_chart(make_trend_chart_plotly(df, date_col, m, brand_color=brand_color, title=title_), use_container_width=True)
        else:
            st.image(png, use_container_width=True)
    else:
        png = make_bar_chart(df, category_col, m, brand_color=brand_color, title=title_)
        chart_images.append((title_, png))
        if use_plotly:
            st.plotly_chart(make_bar_chart_plotly(df, category_col, m, brand_color=brand_color, title=title_), use_container_width=True)
        else:
            st.image(png, use_container_width=True)

if not available_chart_specs:
    st.info("Tidak ada kolom tanggal/kategori dipilih — tidak ada chart yang bisa dibuat.")

current_step = 4

# Gabungkan insight statistik + anomali untuk dimasukkan ke laporan
report_insights = insights + anomaly_insights

# ---------- 6. Export ----------
st.header("6. Export Laporan")

if not can_export():
    st.warning("Jatah ekspor kamu di sesi ini sudah habis. Isi ulang untuk lanjut ekspor:")

    payment_info = get_payment_info()

    if not payment_info:
        st.error("Info pembayaran belum diisi admin (st.secrets['payment']). Silakan hubungi penyedia aplikasi ini.")
    else:
        pay_col1, pay_col2 = st.columns([1, 1])

        with pay_col1:
            st.subheader("💳 Cara Isi Ulang")
            price = payment_info.get("price_per_topup")
            if price:
                st.markdown(f"**Harga:** Rp{price:,} untuk **{EXPORTS_PER_TOPUP}x** ekspor + fitur premium")

            qr_path = payment_info.get("qr_image_path")
            if qr_path:
                try:
                    st.image(qr_path, width=220, caption="Scan pakai DANA / e-wallet lain")
                except Exception:
                    st.caption(f"(Gagal load gambar QR dari path: {qr_path})")

            dana_number = payment_info.get("dana_number")
            dana_name = payment_info.get("dana_name")
            if dana_number:
                st.markdown(f"**Nomor DANA:** `{dana_number}`" + (f" a.n. {dana_name}" if dana_name else ""))

            wa_number = payment_info.get("whatsapp_number")
            if wa_number:
                wa_text = "Halo, saya sudah transfer untuk isi ulang jatah ekspor Generator Laporan Otomatis. Ini bukti transfernya:"
                wa_link = f"https://wa.me/{wa_number}?text={wa_text}".replace(" ", "%20")
                st.link_button("📲 Kirim Bukti Transfer via WhatsApp", wa_link, use_container_width=True)

            st.caption("Setelah transfer & kirim bukti, admin akan verifikasi manual lalu kirimkan kode akses via WhatsApp.")

        with pay_col2:
            st.subheader("🔑 Sudah Punya Kode Akses?")
            with st.form("redeem_form"):
                code_input = st.text_input("Masukkan kode akses dari admin")
                redeem_submitted = st.form_submit_button("Tukar Kode", use_container_width=True)

            if redeem_submitted:
                success, message = redeem_access_code(code_input)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
else:
    watermark_flag = should_show_watermark()
    if watermark_flag:
        st.caption("ℹ️ Versi gratis: laporan akan diberi watermark kecil. Tukar kode akses untuk menghilangkannya.")

    e1, e2, e3 = st.columns(3)

    with e1:
        if st.button("🟠 Generate PPTX", use_container_width=True):
            with st.spinner("Membuat file PowerPoint..."):
                pptx_bytes = generate_pptx(
                    title=report_title, period=period_label, brand_color=brand_color,
                    logo_bytes=logo_bytes, summary=summary, chart_images=chart_images,
                    df_preview=df, insights=report_insights, template=template_choice,
                    lang=lang_choice, watermark=watermark_flag,
                )
                record_export()
                add_report_history(report_title, period_label, "PPTX")
            st.session_state["pptx_bytes"] = pptx_bytes
            st.download_button(
                "⬇️ Download .pptx", data=pptx_bytes,
                file_name=f"{report_title.replace(' ', '_')}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
            )

    with e2:
        if st.button("🔵 Generate PDF", use_container_width=True):
            with st.spinner("Membuat file PDF..."):
                pdf_bytes = generate_pdf(
                    title=report_title, period=period_label, brand_color=brand_color,
                    logo_bytes=logo_bytes, summary=summary, chart_images=chart_images,
                    df_preview=df, insights=report_insights, template=template_choice,
                    lang=lang_choice, watermark=watermark_flag,
                )
                record_export()
                add_report_history(report_title, period_label, "PDF")
            st.session_state["pdf_bytes"] = pdf_bytes
            st.download_button(
                "⬇️ Download .pdf", data=pdf_bytes,
                file_name=f"{report_title.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    with e3:
        excel_locked = not is_premium()
        if excel_locked:
            st.button("🟢 Generate Excel 🔒", use_container_width=True, disabled=True, help="Fitur premium — tukar kode akses dulu")
        else:
            if st.button("🟢 Generate Excel", use_container_width=True):
                with st.spinner("Membuat file Excel..."):
                    excel_bytes = generate_excel(
                        title=report_title, period=period_label, brand_color=brand_color,
                        summary=summary, chart_images=chart_images, df=df,
                    )
                    record_export()
                    add_report_history(report_title, period_label, "Excel")
                st.session_state["excel_bytes"] = excel_bytes
                st.download_button(
                    "⬇️ Download .xlsx", data=excel_bytes,
                    file_name=f"{report_title.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

current_step = 5 if (st.session_state.get("pdf_bytes") or st.session_state.get("pptx_bytes")) else 4

with render_stepper_placeholder.container():
    render_stepper(min(current_step, len(STEPS) - 1))

# ---------- 7. Preview hasil akhir di browser ----------
if st.session_state.get("pdf_bytes") or st.session_state.get("pptx_bytes"):
    st.header("7. Preview Hasil")
    tabs = st.tabs(["Preview PDF", "Preview PPTX"])

    with tabs[0]:
        if st.session_state.get("pdf_bytes"):
            with st.spinner("Merender preview PDF..."):
                images, err = pdf_bytes_to_images(st.session_state["pdf_bytes"])
            if err:
                st.error(f"Gagal merender preview PDF: {err}")
            else:
                for img in images:
                    st.image(img, use_container_width=True)
        else:
            st.caption("Generate PDF dulu di atas untuk melihat preview di sini.")

    with tabs[1]:
        if st.session_state.get("pptx_bytes"):
            with st.spinner("Merender preview PPTX (konversi via LibreOffice)..."):
                images, err = pptx_bytes_to_images(st.session_state["pptx_bytes"])
            if err:
                st.error(f"Gagal merender preview PPTX: {err}")
            else:
                for img in images:
                    st.image(img, use_container_width=True)
        else:
            st.caption("Generate PPTX dulu di atas untuk melihat preview di sini.")

st.divider()
st.caption("MVP — sumber data: upload CSV/Excel atau Google Sheets. Riwayat & profil branding tersimpan sementara (per sesi browser).")
