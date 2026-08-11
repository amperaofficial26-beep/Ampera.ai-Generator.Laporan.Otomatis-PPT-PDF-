"""
Modul untuk menghasilkan ringkasan naratif otomatis (insight) dari data performa:
- Perbandingan periode (paruh pertama vs paruh kedua rentang tanggal)
- Kategori/kampanye dengan performa terbaik & terburuk
"""
import pandas as pd


def _pct_change(old, new):
    if old == 0:
        return None
    return (new - old) / old * 100


def generate_period_insights(df: pd.DataFrame, date_col: str, metric_cols: list) -> list:
    """
    Bandingkan paruh pertama vs paruh kedua rentang tanggal untuk tiap metrik.
    Return list of insight strings (Bahasa Indonesia).
    """
    insights = []
    if date_col not in df.columns or df[date_col].isna().all():
        return insights

    df_sorted = df.dropna(subset=[date_col]).sort_values(date_col)
    if len(df_sorted) < 4:
        return insights

    mid = len(df_sorted) // 2
    first_half = df_sorted.iloc[:mid]
    second_half = df_sorted.iloc[mid:]

    for m in metric_cols:
        if m not in df_sorted.columns:
            continue
        old_val = first_half[m].sum()
        new_val = second_half[m].sum()
        change = _pct_change(old_val, new_val)
        if change is None:
            continue
        arrow = "naik" if change > 0 else "turun"
        insights.append(
            f"**{m}** {arrow} **{abs(change):.1f}%** pada paruh kedua periode "
            f"dibanding paruh pertama ({old_val:,.0f} → {new_val:,.0f})."
        )
    return insights


def generate_category_insights(df: pd.DataFrame, category_col: str, metric_cols: list) -> list:
    """
    Cari kategori dengan nilai tertinggi & terendah untuk tiap metrik.
    Return list of insight strings.
    """
    insights = []
    if not category_col or category_col not in df.columns or not metric_cols:
        return insights

    for m in metric_cols:
        if m not in df.columns:
            continue
        grouped = df.groupby(category_col)[m].sum().sort_values(ascending=False)
        if grouped.empty:
            continue
        top_name, top_val = grouped.index[0], grouped.iloc[0]
        bottom_name, bottom_val = grouped.index[-1], grouped.iloc[-1]
        if top_name == bottom_name:
            continue
        insights.append(
            f"Untuk **{m}**, performa tertinggi ada di **{top_name}** ({top_val:,.0f}), "
            f"sementara **{bottom_name}** paling rendah ({bottom_val:,.0f})."
        )
    return insights


def generate_all_insights(df: pd.DataFrame, date_col: str, metric_cols: list, category_col: str = None) -> list:
    """Gabungkan semua jenis insight jadi satu list."""
    insights = []
    if date_col and date_col != "(tidak ada)":
        insights.extend(generate_period_insights(df, date_col, metric_cols))
    if category_col and category_col != "(tidak ada)":
        insights.extend(generate_category_insights(df, category_col, metric_cols))
    return insights


def generate_metric_deltas(df: pd.DataFrame, date_col: str, metric_cols: list) -> dict:
    """
    Hitung total & persentase perubahan (paruh pertama vs kedua) per metrik,
    dalam bentuk terstruktur (bukan teks) untuk dipakai di st.metric() / metric cards.
    Return: {metric_name: {"total": float, "delta_pct": float | None}}
    """
    result = {}
    has_date = date_col and date_col != "(tidak ada)" and date_col in df.columns and not df[date_col].isna().all()

    df_sorted = None
    if has_date:
        df_sorted = df.dropna(subset=[date_col]).sort_values(date_col)

    for m in metric_cols:
        if m not in df.columns:
            continue
        total = float(df[m].sum())
        delta_pct = None
        if df_sorted is not None and len(df_sorted) >= 4:
            mid = len(df_sorted) // 2
            old_val = df_sorted.iloc[:mid][m].sum()
            new_val = df_sorted.iloc[mid:][m].sum()
            delta_pct = _pct_change(old_val, new_val)
        result[m] = {"total": total, "delta_pct": delta_pct}
    return result

def generate_narrative_summary(report_title: str, period: str, summary: dict,
                                period_insights: list, category_insights: list) -> str:
    """
    Rangkai insight statistik yang sudah dihitung jadi 1 paragraf naratif Bahasa Indonesia,
    murni pakai rule-based (tanpa panggil API/AI apapun -- jadi gratis & tanpa biaya).
    """
    if not summary:
        return ""

    parts = []
    metric_names = list(summary.keys())

    if len(metric_names) == 1:
        metric_intro = f"metrik **{metric_names[0]}**"
    elif len(metric_names) == 2:
        metric_intro = f"metrik **{metric_names[0]}** dan **{metric_names[1]}**"
    else:
        metric_intro = f"{len(metric_names)} metrik utama ({', '.join(metric_names[:-1])}, dan {metric_names[-1]})"

    opening = f"Laporan **{report_title}** untuk periode **{period}** ini merangkum performa {metric_intro}."
    parts.append(opening)

    # Ambil 1-2 insight periode paling signifikan (persentase perubahan terbesar)
    if period_insights:
        parts.append(period_insights[0].replace("**", "**"))
        if len(period_insights) > 1:
            parts.append(period_insights[1])

    # Ambil 1 insight kategori kalau ada
    if category_insights:
        parts.append(category_insights[0])

    closing = "Detail lengkap per metrik dan visualisasi tren dapat dilihat pada bagian berikutnya."
    parts.append(closing)

    return " ".join(parts)
