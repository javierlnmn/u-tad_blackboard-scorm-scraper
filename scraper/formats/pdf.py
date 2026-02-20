from __future__ import annotations

import html
from abc import ABC, abstractmethod
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from scraper.config import _PROJECT_ROOT

_LINESEED_REGULAR = _PROJECT_ROOT / 'assets' / 'fonts' / 'line-seed-jp' / 'LINESeedJP-Regular.ttf'
_PDF_FONT: str = 'Helvetica'
if _LINESEED_REGULAR.exists():
    try:
        pdfmetrics.registerFont(TTFont('LINESeedJP', str(_LINESEED_REGULAR)))
        _PDF_FONT = 'LINESeedJP'
    except Exception:
        pass


class PDFTheme(ABC):
    """Base theme for PDF output. Override to create custom themes."""

    name: str = 'default'

    def __init__(self) -> None:
        styles = getSampleStyleSheet()
        try:
            pdfmetrics.getFont(_PDF_FONT)
            font_name = _PDF_FONT
        except Exception:
            font_name = 'Helvetica'

        self.title = ParagraphStyle(
            'ThemeTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=22,
            textColor=colors.HexColor(self._title_color),
            spaceAfter=4,
        )

        self.heading = ParagraphStyle(
            'ThemeHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=16,
            textColor=colors.HexColor(self._heading_color),
            spaceAfter=3,
        )

        self.subheading = ParagraphStyle(
            'ThemeSubheading',
            parent=styles['Heading3'],
            fontName=font_name,
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
        self.table_header_fg = colors.white
        self.table_grid = colors.grey

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


class OceanTheme(PDFTheme):
    """Blue ocean theme (default)."""

    name = 'ocean'

    @property
    def _title_color(self) -> str:
        return '#1F4E79'

    @property
    def _heading_color(self) -> str:
        return '#2E75B6'

    @property
    def _table_header_bg(self) -> str:
        return '#1F4E79'


class ForestTheme(PDFTheme):
    """Green forest theme."""

    name = 'forest'

    @property
    def _title_color(self) -> str:
        return '#1B4332'

    @property
    def _heading_color(self) -> str:
        return '#2D6A4F'

    @property
    def _table_header_bg(self) -> str:
        return '#1B4332'


class SlateTheme(PDFTheme):
    """Muted slate/grey theme."""

    name = 'slate'

    @property
    def _title_color(self) -> str:
        return '#334155'

    @property
    def _heading_color(self) -> str:
        return '#64748B'

    @property
    def _table_header_bg(self) -> str:
        return '#334155'


class CrimsonTheme(PDFTheme):
    """Red/crimson accent theme."""

    name = 'crimson'

    @property
    def _title_color(self) -> str:
        return '#7F1D1D'

    @property
    def _heading_color(self) -> str:
        return '#B91C1C'

    @property
    def _table_header_bg(self) -> str:
        return '#7F1D1D'


_THEME_REGISTRY: dict[str, type[PDFTheme]] = {
    'default': OceanTheme,
    OceanTheme.name: OceanTheme,
    ForestTheme.name: ForestTheme,
    SlateTheme.name: SlateTheme,
    CrimsonTheme.name: CrimsonTheme,
}


def register_theme(theme_class: type[PDFTheme]) -> None:
    """Register a custom theme for use by name."""
    _THEME_REGISTRY[theme_class.name] = theme_class


def get_theme(name: str) -> PDFTheme:
    """Get a theme instance by name."""
    cls = _THEME_REGISTRY.get((name or '').lower().strip())
    if cls is None:
        return OceanTheme()
    return cls()


def list_themes() -> list[str]:
    """Return available theme names."""
    return list(_THEME_REGISTRY.keys())


def _safe_text(text: str) -> str:
    """Escape text for reportlab Paragraph (avoids HTML interpretation)."""
    return html.escape(text or '', quote=True)


class PDFBuilder:
    """Build a PDF document with reportlab."""

    def __init__(
        self,
        output_path: Path | None = None,
        *,
        theme: PDFTheme | None = None,
        elements: list | None = None,
    ) -> None:
        self.elements = elements if elements is not None else []
        self.theme = theme or OceanTheme()
        self.doc = SimpleDocTemplate(str(output_path), pagesize=A4)

    def add_elements(self, flowables: list) -> None:
        """Append flowables to the builder's elements list."""
        self.elements.extend(flowables)

    def build_title(self, text: str) -> list:
        return [Paragraph(_safe_text(text), self.theme.title), Spacer(1, 0.08 * inch)]

    def build_heading(self, text: str) -> list:
        return [Paragraph(_safe_text(text), self.theme.heading), Spacer(1, 0.06 * inch)]

    def build_subheading(self, text: str) -> list:
        return [Paragraph(_safe_text(text), self.theme.subheading), Spacer(1, 0.04 * inch)]

    def build_paragraph(self, text: str) -> list:
        return [Paragraph(_safe_text(text), self.theme.normal)]

    def build_bullet_list(self, items: list[str]) -> list:
        flow = ListFlowable(
            [ListItem(Paragraph(_safe_text(i), self.theme.normal)) for i in items],
            bulletType='bullet',
        )
        return [flow, Spacer(1, 0.1 * inch)]

    def build_numbered_list(self, items: list[str]) -> list:
        flow = ListFlowable(
            [ListItem(Paragraph(_safe_text(i), self.theme.normal)) for i in items],
            bulletType='1',
        )
        return [flow, Spacer(1, 0.1 * inch)]

    def build_table(self, data: list[list[str]]) -> list:
        escaped = [[_safe_text(cell) for cell in row] for row in data]
        table = Table(escaped)
        table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), self.theme.table_header_bg),
                    ('TEXTCOLOR', (0, 0), (-1, 0), self.theme.table_header_fg),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.theme.table_grid),
                ]
            )
        )
        return [table, Spacer(1, 0.3 * inch)]

    def build_image(self, path: Path, width: float = 4 * inch) -> list:
        img = Image(str(path))
        img.drawWidth = width
        img.drawHeight = width * img.imageHeight / img.imageWidth
        return [img, Spacer(1, 0.2 * inch)]

    def build_spacer(self, height: float = 0.2 * inch) -> list:
        return [Spacer(1, height)]

    def build_page_break(self) -> list:
        return [PageBreak()]

    def build(self) -> None:
        if self.doc:
            self.doc.build(self.elements)


def write_course(course, output_path: Path, *, assets_dir: Path) -> None:
    """Write course as PDF."""
    from reportlab.lib.units import inch

    builder = PDFBuilder(output_path)
    builder.add_elements(builder.build_title(course.title))
    builder.add_elements(builder.build_spacer(0.1 * inch))

    for section_idx, section in enumerate(course.sections, start=1):
        if section_idx > 1:
            builder.add_elements(builder.build_page_break())
        builder.add_elements(builder.build_heading(f'{section_idx}. {section.title}'))
        builder.add_elements(builder.build_spacer(0.06 * inch))

        for lesson_idx, lesson in enumerate(section.lessons, start=1):
            lesson_flowables = builder.build_subheading(f'{section_idx}.{lesson_idx} {lesson.title}')

            for block in lesson.blocks:
                lesson_flowables.extend(block._render_pdf(builder, assets_dir=assets_dir))

            builder.add_elements(lesson_flowables)

        builder.add_elements(builder.build_spacer(0.08 * inch))

    builder.build()
