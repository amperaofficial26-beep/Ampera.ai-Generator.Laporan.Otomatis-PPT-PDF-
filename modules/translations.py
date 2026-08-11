"""
Dictionary terjemahan label-label tetap di laporan (heading, judul section) untuk
mode dwibahasa Indonesia/Inggris. Ini terjemahan LABEL TEMPLATE saja (misal "Ringkasan
Performa" -> "Performance Summary") -- bukan menerjemahkan isi data/insight secara utuh
(itu perlu AI, dan kita hindari karena biaya). Insight naratif tetap dalam Bahasa Indonesia
walau mode EN dipilih, kecuali label section-nya.
"""

LABELS = {
    "id": {
        "summary_heading": "Ringkasan Performa",
        "insight_heading": "Insight & Analisis",
        "detail_heading": "Detail Data",
        "total": "Total",
        "average": "Rata-rata",
        "min": "Min",
        "max": "Max",
        "metric": "Metrik",
    },
    "en": {
        "summary_heading": "Performance Summary",
        "insight_heading": "Insights & Analysis",
        "detail_heading": "Data Detail",
        "total": "Total",
        "average": "Average",
        "min": "Min",
        "max": "Max",
        "metric": "Metric",
    },
}


def get_labels(lang: str = "id") -> dict:
    return LABELS.get(lang, LABELS["id"])
