"""
Modul untuk generate laporan PDF dari data, chart, dan branding user menggunakan reportlab.
Mendukung 3 gaya template: minimalist, corporate, colorful. Mendukung mode dwibahasa ID/EN
dan watermark (versi gratis).
"""
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from modules.translations import get_labels


def _hex_to_color(hex_color: str):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return colors.Color(r / 255, g / 255, b / 255)


def generate_pdf(title: str, period: str, brand_color: str, logo_bytes,
                  summary: dict, chart_images: list, df_preview,
                  insights: list = None, template: str = "corporate", max_rows=15,
                  lang: str = "id", watermark: bool = False) -> bytes:
    """
    chart_images: list of tuples (chart_title, png_bytes)
    template: "minimalist" | "corporate" | "colorful"
    Return: bytes dari file .pdf
    """
    labels = get_labels(lang)
    buf = io.BytesIO()
    brand = _hex_to_color(brand_color)

    def _watermark_canvas(canvas, doc):
        if not watermark:
            return
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#B4B4B4"))
        canvas.drawRightString(doc.pagesize[0] - 1.5 * cm, 0.8 * cm, "Dibuat dengan Generator Laporan Otomatis")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleBrand", parent=styles["Title"], textColor=brand, alignment=TA_LEFT, fontSize=26)
    period_style = ParagraphStyle("Period", parent=styles["Normal"], fontSize=12, textColor=colors.grey)
    heading_style = ParagraphStyle("HeadingBrand", parent=styles["Heading2"], textColor=brand, spaceBefore=6, spaceAfter=10)
    insight_style = ParagraphStyle("Insight", parent=styles["Normal"], fontSize=11, leading=16, spaceAfter=8)

    story = []

    if template == "corporate":
        story.append(HRFlowable(width="100%", thickness=6, color=brand, spaceAfter=14))
    if logo_bytes:
        story.append(Image(io.BytesIO(logo_bytes), width=3 * cm, height=1.5 * cm))
        story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(period, period_style))
    if template == "colorful":
        story.append(Spacer(1, 0.3 * cm))
        story.append(HRFlowable(width="30%", thickness=4, color=brand, hAlign="LEFT"))
    story.append(Spacer(1, 1 * cm))

    if summary:
        story.append(Paragraph(labels["summary_heading"], heading_style))
        table_data = [[labels["metric"], labels["total"], labels["average"], labels["min"], labels["max"]]]
        for name, stats in summary.items():
            table_data.append([
                name,
                f"{stats['total']:,.0f}",
                f"{stats['average']:,.1f}",
                f"{stats['min']:,.0f}",
                f"{stats['max']:,.0f}",
            ])
        tbl = Table(table_data, hAlign="LEFT")
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), brand),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F6FA")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.8 * cm))

    if insights:
        story.append(Paragraph(labels["insight_heading"], heading_style))
        for text in insights[:6]:
            parts = text.split("**")
            formatted = ""
            for idx, part in enumerate(parts):
                formatted += f"<b>{part}</b>" if idx % 2 == 1 else part
            story.append(Paragraph(f"•  {formatted}", insight_style))
        story.append(Spacer(1, 0.5 * cm))

    for chart_title, png_bytes in chart_images:
        story.append(PageBreak())
        story.append(Paragraph(chart_title, heading_style))
        story.append(Image(io.BytesIO(png_bytes), width=22 * cm, height=11 * cm))

    if df_preview is not None and not df_preview.empty:
        story.append(PageBreak())
        story.append(Paragraph(labels["detail_heading"], heading_style))
        display_df = df_preview.head(max_rows)
        data_rows = [list(display_df.columns)] + display_df.astype(str).values.tolist()
        detail_tbl = Table(data_rows, hAlign="LEFT")
        detail_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), brand),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F6FA")]),
        ]))
        story.append(detail_tbl)

    doc.build(story, onFirstPage=_watermark_canvas, onLaterPages=_watermark_canvas)
    buf.seek(0)
    return buf.getvalue()
