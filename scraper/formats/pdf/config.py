"""PDF font and layout configuration."""

from __future__ import annotations

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from scraper.config import _PROJECT_ROOT

MAX_CONTENT_WIDTH = 430

_INTER_REGULAR = _PROJECT_ROOT / 'assets' / 'fonts' / 'inter' / 'Inter-VariableFont_opsz,wght.ttf'
_INTER_BOLD = _PROJECT_ROOT / 'assets' / 'fonts' / 'inter' / 'Inter-Bold.otf'

PDF_FONT: str = 'Helvetica'
PDF_FONT_BOLD: str = 'Helvetica-Bold'

if _INTER_REGULAR.exists():
    try:
        pdfmetrics.registerFont(TTFont('Inter', str(_INTER_REGULAR)))
        PDF_FONT = 'Inter'
        if _INTER_BOLD.exists():
            try:
                pdfmetrics.registerFont(TTFont('Inter-Bold', str(_INTER_BOLD)))
                PDF_FONT_BOLD = 'Inter-Bold'
            except Exception:
                PDF_FONT_BOLD = 'Helvetica-Bold'
        else:
            PDF_FONT_BOLD = 'Helvetica-Bold'
        try:
            pdfmetrics.registerFontFamily('Inter', normal='Inter', bold=PDF_FONT_BOLD)
        except Exception:
            pass
    except Exception:
        pass
