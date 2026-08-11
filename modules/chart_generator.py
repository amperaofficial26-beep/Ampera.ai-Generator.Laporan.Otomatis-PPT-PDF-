"""
Modul untuk membuat chart (line/bar) dari data dan menyimpannya sebagai gambar PNG (bytes).
"""
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _apply_brand_style(fig, ax, brand_color: str):
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(colors="#444444")


def make_trend_chart(df: pd.DataFrame, date_col: str, metric_col: str,
                      brand_color: str = "#2563EB", title: str = None) -> bytes:
    """Buat line chart tren metrik terhadap waktu, return PNG bytes."""
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    ax.plot(df[date_col], df[metric_col], color=brand_color, linewidth=2.2, marker="o", markersize=3)
    ax.set_title(title or f"Tren {metric_col}", fontsize=13, fontweight="bold", color="#1a1a1a", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel(metric_col)
    _apply_brand_style(fig, ax, brand_color)
    fig.autofmt_xdate()
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def make_trend_chart_plotly(df: pd.DataFrame, date_col: str, metric_col: str,
                             brand_color: str = "#2563EB", title: str = None):
    """
    Versi interaktif (Plotly) dari trend chart, khusus untuk preview di browser.
    Return objek Figure Plotly (bukan bytes) -- tampilkan dengan st.plotly_chart(fig).
    """
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[date_col], y=df[metric_col], mode="lines+markers",
        line=dict(color=brand_color, width=2.5),
        marker=dict(size=5),
        hovertemplate=f"%{{x|%d %b %Y}}<br>{metric_col}: %{{y:,.0f}}<extra></extra>",
    ))
    fig.update_layout(
        title=title or f"Tren {metric_col}",
        template="plotly_white",
        margin=dict(l=40, r=20, t=50, b=40),
        height=350,
        hovermode="x unified",
    )
    return fig


def make_bar_chart(df: pd.DataFrame, category_col: str, metric_col: str,
                    brand_color: str = "#2563EB", title: str = None, top_n: int = 10) -> bytes:
    """Buat bar chart perbandingan metrik antar kategori, return PNG bytes."""
    grouped = df.groupby(category_col)[metric_col].sum().sort_values(ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    ax.bar(grouped.index.astype(str), grouped.values, color=brand_color)
    ax.set_title(title or f"{metric_col} per {category_col}", fontsize=13, fontweight="bold", color="#1a1a1a", loc="left")
    ax.set_ylabel(metric_col)
    plt.xticks(rotation=35, ha="right")
    _apply_brand_style(fig, ax, brand_color)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

def make_bar_chart_plotly(df: pd.DataFrame, category_col: str, metric_col: str,
                           brand_color: str = "#2563EB", title: str = None, top_n: int = 10):
    """
    Versi interaktif (Plotly) dari bar chart, khusus untuk preview di browser.
    Return objek Figure Plotly -- tampilkan dengan st.plotly_chart(fig).
    """
    import plotly.graph_objects as go

    grouped = df.groupby(category_col)[metric_col].sum().sort_values(ascending=False).head(top_n)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grouped.index.astype(str), y=grouped.values,
        marker_color=brand_color,
        hovertemplate=f"%{{x}}<br>{metric_col}: %{{y:,.0f}}<extra></extra>",
    ))
    fig.update_layout(
        title=title or f"{metric_col} per {category_col}",
        template="plotly_white",
        margin=dict(l=40, r=20, t=50, b=40),
        height=350,
    )
    return fig
