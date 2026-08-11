"""
Modul deteksi anomali sederhana pakai Z-score (statistik murni, tanpa AI/API).
FITUR PREMIUM.
"""
import pandas as pd
import numpy as np


def detect_anomalies(df: pd.DataFrame, date_col: str, metric_col: str, z_threshold: float = 2.0) -> list:
    """
    Cari titik data yang menyimpang jauh dari rata-rata (Z-score > threshold).
    Return list of dict: {date, value, z_score, direction}.
    """
    if metric_col not in df.columns:
        return []

    data = df.dropna(subset=[metric_col]).copy()
    if len(data) < 5:
        return []

    mean = data[metric_col].mean()
    std = data[metric_col].std()
    if std == 0 or pd.isna(std):
        return []

    data["_z"] = (data[metric_col] - mean) / std
    anomalies = data[data["_z"].abs() >= z_threshold]

    results = []
    for _, row in anomalies.iterrows():
        results.append({
            "date": row[date_col] if date_col and date_col in data.columns else None,
            "value": float(row[metric_col]),
            "z_score": float(row["_z"]),
            "direction": "tinggi" if row["_z"] > 0 else "rendah",
        })
    return results


def generate_anomaly_insights(df: pd.DataFrame, date_col: str, metric_cols: list, z_threshold: float = 2.0) -> list:
    """Rangkai semua anomali per metrik jadi list teks insight Bahasa Indonesia."""
    insights = []
    has_date = date_col and date_col != "(tidak ada)" and date_col in df.columns

    for m in metric_cols:
        anomalies = detect_anomalies(df, date_col if has_date else None, m, z_threshold)
        for a in anomalies[:3]:  # maks 3 per metrik biar nggak kepanjangan
            date_str = f" pada {a['date'].strftime('%d %b %Y')}" if a["date"] is not None else ""
            insights.append(
                f"Terdeteksi anomali di **{m}**{date_str}: nilai **{a['value']:,.0f}** "
                f"({a['direction']} tidak biasa, Z-score {a['z_score']:.1f})."
            )
    return insights
