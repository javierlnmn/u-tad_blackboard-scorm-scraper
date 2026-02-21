from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics

from .config import PDF_FONT, PDF_FONT_BOLD


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
        self.page_bg = colors.HexColor(self._page_bg)

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
        return '#FFFFFF'

    @property
    @abstractmethod
    def _callout_bg(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def _callout_border(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def _page_bg(self) -> str:
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
        return '#D8E8F8'

    @property
    def _callout_border(self) -> str:
        return '#2E75B6'

    @property
    def _page_bg(self) -> str:
        return '#EEEEEE'


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
        return '#D8EBD8'

    @property
    def _callout_border(self) -> str:
        return '#2D6A4F'

    @property
    def _page_bg(self) -> str:
        return '#E8E8E8'


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
        return '#E2E8F0'

    @property
    def _callout_border(self) -> str:
        return '#64748B'

    @property
    def _page_bg(self) -> str:
        return '#E5E7EB'


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
        return '#F5D4D4'

    @property
    def _callout_border(self) -> str:
        return '#B91C1C'

    @property
    def _page_bg(self) -> str:
        return '#EDE8E8'


class ThemeRegistry(Enum):
    OCEAN = OceanTheme
    FOREST = ForestTheme
    SLATE = SlateTheme
    CRIMSON = CrimsonTheme

    def get_theme(self) -> PDFTheme:
        return self.value()

    @classmethod
    def from_name(cls, name: str) -> ThemeRegistry:
        key = (name or '').lower().strip() or 'ocean'
        if key == 'default':
            key = 'ocean'
        try:
            return cls[key.upper()]
        except KeyError:
            return cls.OCEAN

    @classmethod
    def list_themes(cls) -> list[str]:
        return [m.name.lower() for m in cls]
