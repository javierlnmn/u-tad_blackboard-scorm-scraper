from __future__ import annotations

import html
from abc import ABC, abstractmethod
from pathlib import Path

from bs4 import BeautifulSoup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
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
    XPreformatted,
)

from scraper.config import _PROJECT_ROOT

_MAX_CONTENT_WIDTH = 430  # pt, matches text/code block width

_INTER_REGULAR = _PROJECT_ROOT / 'assets' / 'fonts' / 'inter' / 'Inter-VariableFont_opsz,wght.ttf'
_INTER_BOLD = _PROJECT_ROOT / 'assets' / 'fonts' / 'inter' / 'Inter-Bold.otf'
_PDF_FONT: str = 'Helvetica'
_PDF_FONT_BOLD: str = 'Helvetica-Bold'
if _INTER_REGULAR.exists():
    try:
        pdfmetrics.registerFont(TTFont('Inter', str(_INTER_REGULAR)))
        _PDF_FONT = 'Inter'
        if _INTER_BOLD.exists():
            try:
                pdfmetrics.registerFont(TTFont('Inter-Bold', str(_INTER_BOLD)))
                _PDF_FONT_BOLD = 'Inter-Bold'
            except Exception:
                _PDF_FONT_BOLD = 'Helvetica-Bold'
        else:
            _PDF_FONT_BOLD = 'Helvetica-Bold'
        try:
            pdfmetrics.registerFontFamily('Inter', normal='Inter', bold=_PDF_FONT_BOLD)
        except Exception:
            pass
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
        try:
            pdfmetrics.getFont(_PDF_FONT_BOLD)
            font_bold = _PDF_FONT_BOLD
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
        return _text_color_for_bg(self._table_header_bg)

    @property
    @abstractmethod
    def _callout_bg(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def _callout_border(self) -> str:
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
        return '#4A8FCA'  # lighter blue, darker than callout #E8F4FC

    @property
    def _callout_bg(self) -> str:
        return '#E8F4FC'

    @property
    def _callout_border(self) -> str:
        return '#2E75B6'


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
        return '#2D6A4F'  # lighter green, darker than callout #E8F5E9

    @property
    def _callout_bg(self) -> str:
        return '#E8F5E9'

    @property
    def _callout_border(self) -> str:
        return '#2D6A4F'


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
        return '#475569'  # lighter slate, darker than callout #F1F5F9

    @property
    def _callout_bg(self) -> str:
        return '#F1F5F9'

    @property
    def _callout_border(self) -> str:
        return '#64748B'


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
        return '#B91C1C'  # lighter red, darker than callout #FEE2E2

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


def _luminance(hex_color: str) -> float:
    """Relative luminance 0–1. Dark colors ~0.1–0.3, light ~0.9+."""
    h = (hex_color or '').strip().lstrip('#')
    if len(h) == 6:
        r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
        return 0.299 * r + 0.587 * g + 0.114 * b
    return 0.5


def _text_color_for_bg(hex_bg: str) -> str:
    """White if background is dark enough, else black."""
    return '#FFFFFF' if _luminance(hex_bg) < 0.45 else '#000000'


def _safe_text(text: str) -> str:
    """Escape text for reportlab Paragraph (avoids HTML interpretation)."""
    return html.escape(text or '', quote=True)


def _wrap_code_lines(text: str, max_chars: int = 85) -> str:
    """Wrap long lines at word boundaries so code fits within the page (XPreformatted doesn't wrap)."""
    lines = []
    for line in text.split('\n'):
        if len(line) <= max_chars:
            lines.append(line)
            continue
        base_indent = line[: len(line) - len(line.lstrip())]
        rest = line
        while rest:
            if len(rest) <= max_chars:
                lines.append(rest)
                break
            chunk = rest[:max_chars]
            break_at = chunk.rfind(' ')
            if break_at > max_chars // 2:
                head = rest[: break_at + 1].rstrip()
                rest = base_indent + rest[break_at + 1 :].lstrip()
            else:
                head = rest[:max_chars]
                rest = base_indent + rest[max_chars:].lstrip()
            lines.append(head)
    return '\n'.join(lines)


def _link_tag(href: str, link_text: str) -> str:
    safe_href = html.escape(href, quote=True)
    safe_text = html.escape(link_text, quote=True)
    return f'<a href="{safe_href}" color="#2563eb">{safe_text}</a>'


def _html_inline_to_markup(node) -> str:
    """Convert inline HTML to ReportLab Paragraph markup (bold, italic, links)."""
    from bs4 import NavigableString

    if isinstance(node, NavigableString):
        return html.escape(str(node))
    if not hasattr(node, 'name') or not node.name:
        return html.escape(str(node))

    name = node.name.lower()
    if name == 'br':
        return '<br/>'
    if name in {'strong', 'b'}:
        inner = ''.join(_html_inline_to_markup(c) for c in node.contents)
        return f'<b>{inner}</b>' if inner.strip() else inner
    if name in {'em', 'i'}:
        inner = ''.join(_html_inline_to_markup(c) for c in node.contents)
        return f'<i>{inner}</i>' if inner.strip() else inner
    if name == 'a':
        href = (node.get('href') or '').strip()
        label = ''.join(_html_inline_to_markup(c) for c in node.contents).strip()
        label = label or node.get_text(' ', strip=True)
        if href:
            return _link_tag(href, label or href)
        return html.escape(label)
    if name == 'code':
        inner = ''.join(_html_inline_to_markup(c) for c in node.contents)
        return f'<font name="Courier">{html.escape(inner)}</font>'
    return ''.join(_html_inline_to_markup(c) for c in node.contents)


def html_to_flowables(
    html_text: str,
    builder: 'PDFBuilder',
    *,
    assets_dir: Path | None = None,
) -> list:
    """Convert HTML to a list of PDF flowables. Handles bold, italic, links, tables, lists."""
    soup = BeautifulSoup(html_text or '', 'html.parser')
    flowables: list = []

    def render_inline(node) -> str:
        from bs4 import NavigableString

        if isinstance(node, NavigableString):
            return html.escape(str(node))
        if not hasattr(node, 'name'):
            return html.escape(str(node))
        return _html_inline_to_markup(node)

    def render_inline_children(tag) -> str:
        return ''.join(render_inline(c) for c in tag.contents)

    def render_block(node):
        if not hasattr(node, 'name') or not node.name:
            txt = str(node).strip()
            if txt:
                flowables.append(Paragraph(html.escape(txt), builder.theme.normal))
            return

        name = node.name.lower()

        if name == 'table':
            rows = node.find_all('tr')
            if rows:
                col_count = max(len(tr.find_all(['th', 'td'])) for tr in rows) if rows else 0
                data = []
                for tr in rows:
                    cells = tr.find_all(['th', 'td'])
                    row = [render_inline_children(c).strip() for c in cells]
                    row.extend([''] * (col_count - len(row)))
                    data.append(row)
                if data:
                    flowables.extend(builder.build_table(data))
            return

        if name in {'ul', 'ol'}:
            items = []
            for li in node.find_all('li', recursive=False):
                txt = render_inline_children(li).strip()
                if txt:
                    items.append(txt)
            if items:
                if name == 'ol':
                    flowables.extend(builder.build_numbered_list(items))
                else:
                    flowables.extend(builder.build_bullet_list(items))
            return

        if name == 'img':
            src = (node.get('src') or '').strip()
            if assets_dir and src:
                path = assets_dir / Path(src).name
                if not path.exists():
                    for p in assets_dir.rglob(Path(src).name):
                        path = p
                        break
                if path.exists():
                    flowables.extend(builder.build_image(path))
            return

        if name in {'div', 'section', 'article'}:
            for child in node.contents:
                render_block(child)
            return

        if name in {'p', 'span'}:
            txt = render_inline_children(node).strip()
            if txt:
                flowables.append(Paragraph(txt, builder.theme.normal))
            return

        if name == 'pre':
            code = node.get_text('\n', strip=False).rstrip('\n')
            if code.strip():
                flowables.extend(builder.build_code_block(code))
            return

        if name in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            txt = render_inline_children(node).strip()
            if txt:
                if name in {'h1', 'h2'}:
                    flowables.extend(builder.build_heading(txt))
                else:
                    flowables.extend(builder.build_subheading(txt))
            return

        for child in node.contents:
            if hasattr(child, 'name') and child.name:
                render_block(child)
            else:
                txt = str(child).strip()
                if txt:
                    flowables.append(Paragraph(html.escape(txt), builder.theme.normal))

    for child in soup.contents:
        render_block(child)

    return flowables


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

    def build_code_block(self, code: str, language: str | None = None) -> list:
        raw_code = (code or '').strip()
        if not raw_code:
            return []

        raw_code = _wrap_code_lines(raw_code, max_chars=85)
        lang = (language or 'text').strip().lower() or 'text'

        try:
            lexer = get_lexer_by_name(lang, stripall=False)
        except Exception:
            lexer = get_lexer_by_name('text', stripall=False)

        formatter = HtmlFormatter(nowrap=True, noclasses=True)
        highlighted_html = highlight(raw_code, lexer, formatter)
        soup = BeautifulSoup(highlighted_html, 'html.parser')
        pieces: list[str] = []

        def _walk(node) -> None:
            if hasattr(node, 'name') and node.name == 'span':
                style = node.get('style', '')
                color = 'black'
                if 'color:' in style:
                    part = style.split('color:')[-1].split(';')[0].strip()
                    if part:
                        color = part
                text = html.escape(node.get_text())
                pieces.append(f'<font color="{html.escape(color)}">{text}</font>')
            elif hasattr(node, 'children'):
                for child in node.children:
                    _walk(child)
            else:
                s = str(node)
                if s:
                    pieces.append(html.escape(s))

        for child in soup.children:
            _walk(child)
        final_text = ''.join(pieces) or html.escape(raw_code)
        code_style = ParagraphStyle(
            'CodeBlock',
            fontName='Courier',
            fontSize=9,
            leading=11,
        )
        _code_border_col = 12
        _code_content_col = _MAX_CONTENT_WIDTH
        _code_bg = colors.HexColor('#F5F5F5')
        _code_border = colors.HexColor('#9E9E9E')
        lines = final_text.split('\n')
        _lines_per_page = 50
        rows = []
        for i in range(0, len(lines), _lines_per_page):
            chunk = '\n'.join(lines[i : i + _lines_per_page])
            code_flow = XPreformatted(chunk, code_style)
            rows.append([Spacer(_code_border_col, 1), code_flow])
        table = Table(rows, colWidths=[_code_border_col, _code_content_col], cornerRadii=[6, 6, 6, 6])
        table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, -1), _code_bg),
                    ('BACKGROUND', (0, 0), (0, -1), _code_border),
                    ('LEFTPADDING', (0, 0), (0, -1), 4),
                    ('RIGHTPADDING', (0, 0), (0, -1), 4),
                    ('LEFTPADDING', (1, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (1, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]
            )
        )
        return [table, Spacer(1, 0.1 * inch)]

    def build_callout(
        self,
        body: str | None = None,
        href: str | None = None,
        *,
        body_flowables: list | None = None,
        link_text: str | None = None,
    ) -> list:
        content_flowables: list = []
        if body_flowables:
            content_flowables = list(body_flowables)
        elif body:
            body = (body or '').strip()
            if body:
                content_flowables = [Paragraph(body, self.theme.normal)]
        if href:
            label = (link_text or 'Link').strip()
            link_para = Paragraph(_link_tag(href, label), self.theme.normal)
            if content_flowables:
                content_flowables.append(Spacer(1, 0.08 * inch))
            content_flowables.append(link_para)
        if not content_flowables:
            return []

        # Use widths that fit typical A4 frame (~451pt); one row per flowable so table can split
        _border_col = 12
        _content_col = _MAX_CONTENT_WIDTH
        border_cell = Spacer(_border_col, 1)
        rows = [[border_cell, content_flowables[0]]]
        for flow in content_flowables[1:]:
            rows.append([border_cell, flow])
        table = Table(rows, colWidths=[_border_col, _content_col], cornerRadii=[6, 6, 6, 6])
        table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, -1), self.theme.callout_bg),
                    ('BACKGROUND', (0, 0), (0, -1), self.theme.callout_border),
                    ('LEFTPADDING', (0, 0), (0, -1), 4),
                    ('RIGHTPADDING', (0, 0), (0, -1), 4),
                    ('LEFTPADDING', (1, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (1, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]
            )
        )
        return [
            Spacer(1, 0.1 * inch),
            table,
            Spacer(1, 0.1 * inch),
        ]

    def build_bullet_list(self, items: list[str]) -> list:
        flow = ListFlowable(
            [ListItem(Paragraph(i, self.theme.normal)) for i in items],
            bulletType='bullet',
        )
        return [flow, Spacer(1, 0.1 * inch)]

    def build_bullet_list_with_content(
        self, items: list[tuple[str, list]], *, title_bold: bool = True
    ) -> list:
        """Build bullet list where each item has (title, content_flowables)."""
        list_items = []
        for title, content_flowables in items:
            parts: list = []
            if title:
                txt = f'<b>{html.escape(title)}</b>' if title_bold else _safe_text(title)
                parts.append(Paragraph(txt, self.theme.normal))
            if content_flowables:
                parts.append(Spacer(1, 0.02 * inch))
                parts.extend(content_flowables)
            list_items.append(ListItem(parts))
        flow = ListFlowable(list_items, bulletType='bullet')
        return [flow, Spacer(1, 0.1 * inch)]

    def build_numbered_list(self, items: list[str]) -> list:
        flow = ListFlowable(
            [ListItem(Paragraph(i, self.theme.normal)) for i in items],
            bulletType='1',
        )
        return [flow, Spacer(1, 0.1 * inch)]

    def build_numbered_list_with_content(self, items: list[list]) -> list:
        """Build numbered list where each item is a list of flowables."""
        list_items = [ListItem(flows) for flows in items if flows]
        if not list_items:
            return []
        flow = ListFlowable(list_items, bulletType='1')
        return [flow, Spacer(1, 0.1 * inch)]

    def build_table(self, data: list[list[str]]) -> list:
        if not data:
            return []
        ncols = max(len(row) for row in data)
        _table_width = _MAX_CONTENT_WIDTH
        col_widths = [_table_width / ncols] * ncols
        _table_row_alt = colors.HexColor('#F5F5F5')

        header_style = ParagraphStyle(
            'TableHeader',
            parent=self.theme.normal,
            textColor=self.theme.table_header_text_color,
        )

        cells = []
        for r, row in enumerate(data):
            style = header_style if r == 0 else self.theme.normal
            cells.append(
                [Paragraph((c or '').strip(), style) for c in row]
                + [Paragraph('', style)] * (ncols - len(row))
            )
        table = Table(cells, colWidths=col_widths, cornerRadii=[3, 3, 3, 3])
        table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), self.theme.table_header_bg),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, _table_row_alt]),
                    ('GRID', (0, 0), (-1, -1), 0.5, self.theme.table_grid),
                ]
            )
        )
        return [table, Spacer(1, 0.3 * inch)]

    def build_image(self, path: Path, width: float | None = None) -> list:
        img = Image(str(path), hAlign='CENTER')
        w = width if width is not None else _MAX_CONTENT_WIDTH
        img.drawWidth = min(w, img.imageWidth)
        img.drawHeight = img.drawWidth * img.imageHeight / img.imageWidth
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
