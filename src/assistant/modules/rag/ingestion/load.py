"""Load PDF files into (text, metadata) pairs."""

from pathlib import Path

from pypdf import PdfReader


def load_pdf(path: Path) -> list[tuple[str, dict]]:
    """Read a PDF and return one (text, metadata) tuple per page."""
    reader = PdfReader(str(path))
    pages = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append((text, {"source": path.name, "page": page_num}))
    return pages
