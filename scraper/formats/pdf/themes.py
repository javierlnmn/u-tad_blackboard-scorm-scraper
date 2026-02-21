from __future__ import annotations

from abc import ABC, abstractmethod

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics

from .config import PDF_FONT, PDF_FONT_BOLD
from .utils import text_color_for_bg


class PDFTheme(ABC):
    name: str = 'default'

    def __init__(self) -> None:
        styles = getSampleStyleSheet()
        try:
            pdfmetrics.getFont(PDF_FONT)
            font_name = PDF_FONT
        except Exception:
            font_name = 'Helvetica'
        try:
            pdfmetrics.getFont(PDF_FONT_BOLD)
            font_bold = PDF_FONT_BOLD
        except Exception:
            font_bold = 'Helvetica-Bold'

        self.title = ParagraphStyle(
            'ThemeTitle',
            parent=styles['Heading1'],
            fontName=font_bold,
            fontSize=22,
            textColor=colors.HexColor(self._title_color),
            spaceAfter=4,
        )

        self.heading = ParagraphStyle(
            'ThemeHeading',
            parent=styles['Heading2'],
            fontName=font_bold,
            fontSize=16,
            textColor=colors.HexColor(self._heading_color),
            spaceAfter=3,
        )

        self.subheading = ParagraphStyle(
            'ThemeSubheading',
            parent=styles['Heading3'],
            fontName=font_bold,
            fontSize=13,
            textColor=colors.HexColor(self._heading_color),
            spaceAfter=2,
        )

        self.normal = ParagraphStyle(
            'ThemeNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=11,
            leading=15,
            spaceAfter=4,
        )

        self.table_header_bg = colors.HexColor(self._table_header_bg)
        self.table_header_text_color = colors.HexColor(self._table_header_text_color)
        self.table_grid = colors.grey
        self.callout_bg = colors.HexColor(self._callout_bg)
        self.callout_border = colors.HexColor(self._callout_border)

    @property
    @abstractmethod
    def _title_color(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def _heading_color(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def _table_header_bg(self) -> str:
        raise NotImplementedError

    @property
    def _table_header_text_color(self) -> str:
        return text_color_for_bg(self._table_header_bg)

    @property
    @abstractmethod
    def _callout_bg(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def _callout_border(self) -> str:
        raise NotImplementedError


class OceanTheme(PDFTheme):
    name = 'ocean'

    @property
    def _title_color(self) -> str:
        return '#1F4E79'

    @property
    def _heading_color(self) -> str:
        return '#2E75B6'

    @property
    def _table_header_bg(self) -> str:
        return '#4A8FCA'

    @property
    def _callout_bg(self) -> str:
        return '#E8F4FC'

    @property
    def _callout_border(self) -> str:
        return '#2E75B6'


class ForestTheme(PDFTheme):
    name = 'forest'

    @property
    def _title_color(self) -> str:
        return '#1B4332'

    @property
    def _heading_color(self) -> str:
        return '#2D6A4F'

    @property
    def _table_header_bg(self) -> str:
        return '#2D6A4F'

    @property
    def _callout_bg(self) -> str:
        return '#E8F5E9'

    @property
    def _callout_border(self) -> str:
        return '#2D6A4F'


class SlateTheme(PDFTheme):
    name = 'slate'

    @property
    def _title_color(self) -> str:
        return '#334155'

    @property
    def _heading_color(self) -> str:
        return '#64748B'

    @property
    def _table_header_bg(self) -> str:
        return '#475569'

    @property
    def _callout_bg(self) -> str:
        return '#F1F5F9'

    @property
    def _callout_border(self) -> str:
        return '#64748B'


class CrimsonTheme(PDFTheme):
    name = 'crimson'

    @property
    def _title_color(self) -> str:
        return '#7F1D1D'

    @property
    def _heading_color(self) -> str:
        return '#B91C1C'

    @property
    def _table_header_bg(self) -> str:
        return '#B91C1C'

    @property
    def _callout_bg(self) -> str:
        return '#FEE2E2'

    @property
    def _callout_border(self) -> str:
        return '#B91C1C'


_THEME_REGISTRY: dict[str, type[PDFTheme]] = {
    'default': OceanTheme,
    OceanTheme.name: OceanTheme,
    ForestTheme.name: ForestTheme,
    SlateTheme.name: SlateTheme,
    CrimsonTheme.name: CrimsonTheme,
}


def register_theme(theme_class: type[PDFTheme]) -> None:
    _THEME_REGISTRY[theme_class.name] = theme_class


def get_theme(name: str) -> PDFTheme:
    cls = _THEME_REGISTRY.get((name or '').lower().strip())
    if cls is None:
        return OceanTheme()
    return cls()


def list_themes() -> list[str]:
    return list(_THEME_REGISTRY.keys())
