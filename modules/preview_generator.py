"""
Modul untuk membuat preview visual dari file PDF/PPTX yang sudah digenerate,
supaya user bisa lihat hasilnya langsung di browser sebelum download.
"""
import io
import subprocess
import tempfile
import os


def pdf_bytes_to_images(pdf_bytes: bytes, max_pages: int = 6, dpi: int = 100):
    """Render halaman PDF (bytes) jadi list gambar PNG (bytes), pakai pdf2image (poppler)."""
    from pdf2image import convert_from_bytes
    try:
        pages = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=1, last_page=max_pages)
    except Exception as e:
        return [], str(e)

    images = []
    for page in pages:
        buf = io.BytesIO()
        page.save(buf, format="PNG")
        images.append(buf.getvalue())
    return images, None


def pptx_bytes_to_pdf_bytes(pptx_bytes: bytes, timeout: int = 60):
    """
    Konversi .pptx (bytes) ke .pdf (bytes) menggunakan LibreOffice headless.
    Return (pdf_bytes, error_message). Kalau gagal, pdf_bytes = None dan error_message terisi.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        pptx_path = os.path.join(tmp_dir, "input.pptx")
        with open(pptx_path, "wb") as f:
            f.write(pptx_bytes)

        try:
            result = subprocess.run(
                ["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp_dir, pptx_path],
                capture_output=True, text=True, timeout=timeout
            )
        except FileNotFoundError:
            return None, "LibreOffice (soffice) tidak ditemukan di server. Preview PPTX tidak tersedia."
        except subprocess.TimeoutExpired:
            return None, "Konversi PPTX ke gambar preview memakan waktu terlalu lama."

        pdf_path = os.path.join(tmp_dir, "input.pdf")
        if not os.path.exists(pdf_path):
            return None, f"Gagal konversi PPTX: {result.stderr[:300]}"

        with open(pdf_path, "rb") as f:
            return f.read(), None


def pptx_bytes_to_images(pptx_bytes: bytes, max_pages: int = 6, dpi: int = 100):
    """Render slide PPTX (bytes) jadi list gambar PNG (bytes): PPTX -> PDF -> gambar."""
    pdf_bytes, err = pptx_bytes_to_pdf_bytes(pptx_bytes)
    if pdf_bytes is None:
        return [], err
    return pdf_bytes_to_images(pdf_bytes, max_pages=max_pages, dpi=dpi)
