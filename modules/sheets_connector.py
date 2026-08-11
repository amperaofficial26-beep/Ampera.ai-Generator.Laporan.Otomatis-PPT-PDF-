"""
Modul untuk narik data dari Google Sheets TANPA perlu OAuth/API key -- caranya lewat
link "Publish to web" (File > Share > Publish to web > pilih format CSV) dari Google Sheets.
FITUR PREMIUM.

Kenapa bukan Google Sheets API resmi? API resmi butuh OAuth consent screen + service account
setup yang cukup ribet buat MVP. Cara publish-to-web ini jauh lebih simpel buat user awam,
dengan trade-off: sheet-nya jadi bisa diakses siapa saja yang punya link (read-only).
"""
import pandas as pd
import re


def is_google_sheets_url(url: str) -> bool:
    return bool(re.search(r"docs\.google\.com/spreadsheets", url))


def build_csv_export_url(sheet_url: str) -> str:
    """
    Ubah berbagai bentuk URL Google Sheets jadi URL export CSV langsung.
    Mendukung: link edit biasa, link publish-to-web, dan link yang sudah CSV.
    """
    if "output=csv" in sheet_url or "/pub?" in sheet_url and "csv" in sheet_url:
        return sheet_url

    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
    if not match:
        raise ValueError("URL Google Sheets tidak dikenali. Pastikan link lengkap dari address bar.")

    sheet_id = match.group(1)
    gid_match = re.search(r"[#&]gid=(\d+)", sheet_url)
    gid = gid_match.group(1) if gid_match else "0"

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def fetch_google_sheet(sheet_url: str) -> tuple:
    """
    Ambil data dari Google Sheets sebagai DataFrame.
    Return: (df, error_message). Kalau gagal, df = None.
    """
    if not is_google_sheets_url(sheet_url):
        return None, "URL yang dimasukkan bukan link Google Sheets."

    try:
        csv_url = build_csv_export_url(sheet_url)
        df = pd.read_csv(csv_url)
        if df.empty:
            return None, "Sheet berhasil diakses tapi datanya kosong."
        df.columns = [str(c).strip() for c in df.columns]
        return df, None
    except ValueError as e:
        return None, str(e)
    except Exception as e:
        return None, (
            f"Gagal mengambil data ({e}). Pastikan sheet sudah di-share dengan akses "
            "'Anyone with the link' (minimal Viewer), atau sudah di-Publish to web."
        )
