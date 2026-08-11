"""
Modul proyeksi tren sederhana pakai regresi linear (numpy polyfit).
FITUR PREMIUM -- murni matematika/statistik, TIDAK memanggil API/AI apapun, jadi tidak ada biaya.
"""
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def forecast_metric(df: pd.DataFrame, date_col: str, metric_col: str, forecast_days: int = 30) -> dict:
    """
    Proyeksi nilai metrik ke depan pakai regresi linear sederhana atas data historis.
    Return dict berisi angka proyeksi & data untuk chart. Kalau data kurang, return None.
    """
    data = df.dropna(subset=[date_col, metric_col]).sort_values(date_col)
    if len(data) < 5:
        return None

    x = (data[date_col] - data[date_col].min()).dt.days.values.astype(float)
    y = data[metric_col].values.astype(float)

    # Regresi linear derajat 1 (y = a*x + b)
    coeffs = np.polyfit(x, y, 1)
    slope, intercept = coeffs[0], coeffs[1]

    last_x = x.max()
    last_date = data[date_col].max()
    future_x = np.arange(last_x + 1, last_x + 1 + forecast_days)
    future_y = slope * future_x + intercept
    future_y = np.clip(future_y, a_min=0, a_max=None)  # nggak masuk akal kalau negatif
    future_dates = [last_date + pd.Timedelta(days=int(d - last_x)) for d in future_x]

    trend_direction = "naik" if slope > 0 else ("turun" if slope < 0 else "stabil")
    projected_total = float(future_y.sum())
    current_avg_daily = float(y.mean())
    projected_avg_daily = float(future_y.mean())

    return {
        "historical_dates": data[date_col].tolist(),
        "historical_values": y.tolist(),
        "future_dates": future_dates,
        "future_values": future_y.tolist(),
        "trend_direction": trend_direction,
        "projected_total": projected_total,
        "current_avg_daily": current_avg_daily,
        "projected_avg_daily": projected_avg_daily,
        "forecast_days": forecast_days,
    }


def make_forecast_chart(metric_col: str, forecast_result: dict, brand_color: str = "#2563EB") -> bytes:
    """Buat chart historis + garis proyeksi (putus-putus), return PNG bytes."""
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)

    ax.plot(forecast_result["historical_dates"], forecast_result["historical_values"],
            color=brand_color, linewidth=2, label="Data Historis")
    ax.plot(forecast_result["future_dates"], forecast_result["future_values"],
            color=brand_color, linewidth=2, linestyle="--", alpha=0.6,
            label=f"Proyeksi {forecast_result['forecast_days']} Hari")

    ax.set_title(f"Proyeksi Tren: {metric_col}", fontsize=13, fontweight="bold", color="#1a1a1a", loc="left")
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def generate_forecast_text(metric_col: str, forecast_result: dict) -> str:
    """Teks ringkas hasil proyeksi, rule-based (bukan AI)."""
    direction_word = {"naik": "meningkat", "turun": "menurun", "stabil": "relatif stabil"}[forecast_result["trend_direction"]]
    return (
        f"Berdasarkan tren {forecast_result['forecast_days']} hari terakhir, **{metric_col}** diproyeksikan "
        f"**{direction_word}** dengan rata-rata harian sekitar **{forecast_result['projected_avg_daily']:,.0f}** "
        f"(dibanding rata-rata historis **{forecast_result['current_avg_daily']:,.0f}**), "
        f"dengan estimasi total **{forecast_result['projected_total']:,.0f}** dalam {forecast_result['forecast_days']} hari ke depan. "
        f"*(Proyeksi linear sederhana, bukan prediksi pasti -- gunakan sebagai referensi awal.)*"
    )
