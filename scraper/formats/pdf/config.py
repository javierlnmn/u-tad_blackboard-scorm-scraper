from __future__ import annotations

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from scraper.config import _PROJECT_ROOT

MAX_CONTENT_WIDTH = 430

_FONTS_DIR = _PROJECT_ROOT / 'assets' / 'fonts'
_INTER_REGULAR = _FONTS_DIR / 'inter' / 'Inter-VariableFont_opsz,wght.ttf'
_INTER_BOLD = _FONTS_DIR / 'inter' / 'Inter-Bold.otf'
_JP_REGULAR = _FONTS_DIR / 'line-seed-jp' / 'LINESeedJP-Regular.ttf'
_JP_BOLD = _FONTS_DIR / 'line-seed-jp' / 'LINESeedJP-Bold.ttf'
_JETBRAINS_FONT = _FONTS_DIR / 'jetbrains-mono' / 'JetBrainsMono-Regular.ttf'

PDF_FONT_INTER: str = 'Helvetica'
PDF_FONT_INTER_BOLD: str = 'Helvetica-Bold'
PDF_FONT_JP: str = 'Helvetica'
PDF_FONT_JP_BOLD: str = 'Helvetica-Bold'
PDF_FONT_JETBRAINS: str = 'Courier'

if _INTER_REGULAR.exists() and _INTER_BOLD.exists():
    try:
        pdfmetrics.registerFont(TTFont('Inter', str(_INTER_REGULAR)))
        pdfmetrics.registerFont(TTFont('Inter-Bold', str(_INTER_BOLD)))
        PDF_FONT_INTER = 'Inter'
        PDF_FONT_INTER_BOLD = 'Inter-Bold'
        pdfmetrics.registerFontFamily('Inter', normal='Inter', bold='Inter-Bold')
    except Exception:
        pass

if _JP_REGULAR.exists() and _JP_BOLD.exists():
    try:
        pdfmetrics.registerFont(TTFont('LINESeedJP', str(_JP_REGULAR)))
        pdfmetrics.registerFont(TTFont('LINESeedJP-Bold', str(_JP_BOLD)))
        PDF_FONT_JP = 'LINESeedJP'
        PDF_FONT_JP_BOLD = 'LINESeedJP-Bold'
        pdfmetrics.registerFontFamily('LINESeedJP', normal='LINESeedJP', bold='LINESeedJP-Bold')
    except Exception:
        pass

if _JETBRAINS_FONT.exists():
    try:
        pdfmetrics.registerFont(TTFont('JetBrainsMono', str(_JETBRAINS_FONT)))
        PDF_FONT_JETBRAINS = 'JetBrainsMono'
    except Exception:
        pass
