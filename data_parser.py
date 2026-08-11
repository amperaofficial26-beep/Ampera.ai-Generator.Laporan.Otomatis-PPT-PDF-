"""
Modul untuk parsing file data (CSV/Excel) dan auto-deteksi tipe kolom.
"""
import pandas as pd


def load_data(uploaded_file):
    """Baca file CSV atau Excel jadi DataFrame."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    else:
        raise ValueError("Format file tidak didukung. Gunakan CSV atau Excel.")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def detect_columns(df: pd.DataFrame):
    """
    Auto-deteksi kolom tanggal, numerik, dan kategori dari sebuah DataFrame.
    Return dict berisi list nama kolom per kategori, plus tebakan terbaik.
    """
    date_cols, numeric_cols, categorical_cols = [], [], []

    for col in df.columns:
        series = df[col]

        # Coba deteksi kolom tanggal
        if pd.api.types.is_datetime64_any_dtype(series):
            date_cols.append(col)
            continue
        if series.dtype == object:
            try:
                parsed = pd.to_datetime(series, errors="coerce", format=None)
                # kalau sebagian besar berhasil di-parse, anggap kolom tanggal
                if parsed.notna().mean() > 0.8:
                    date_cols.append(col)
                    continue
            except Exception:
                pass

        # Numerik
        if pd.api.types.is_numeric_dtype(series):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    best_date = date_cols[0] if date_cols else None
    best_metrics = numeric_cols[:3] if numeric_cols else []

    return {
        "date_cols": date_cols,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
        "suggested_date": best_date,
        "suggested_metrics": best_metrics,
    }


def coerce_date_column(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Pastikan kolom tanggal terpilih benar-benar bertipe datetime, lalu urutkan."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.sort_values(date_col)
    return df


def summarize_metrics(df: pd.DataFrame, metric_cols: list) -> dict:
    """Ringkasan sederhana (total, rata-rata, min, max) untuk tiap metrik numerik."""
    summary = {}
    for col in metric_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        summary[col] = {
            "total": float(series.sum()),
            "average": float(series.mean()),
            "min": float(series.min()),
            "max": float(series.max()),
        }
    return summary
