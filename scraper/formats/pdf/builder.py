from __future__ import annotations

import html
import re
from pathlib import Path

from pygments import lex
from pygments.lexers import get_lexer_by_name
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
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

from scraper.formats.base import CourseBuilder

from .config import MAX_CONTENT_WIDTH, MAX_IMAGE_HEIGHT, PDF_FONT_JETBRAINS
from .themes import OceanTheme, PDFTheme
from .utils import link_tag, safe_text, wrap_code_lines

_DEFAULT_CODE_STYLE = 'pastie'


def _parse_color_from_style(style_str: str) -> str | None:
    """Extract hex text color from Pygments style string (e.g. 'italic #888' -> '#888888')."""
    if not style_str:
        return None
    for part in style_str.split():
        part = part.strip()
        if part.startswith('#') and 'bg:' not in part.lower():
            hex_val = part.lstrip('#')
            if len(hex_val) in (3, 6) and all(c in '0123456789abcdefABCDEF' for c in hex_val):
                if len(hex_val) == 3:
                    hex_val = ''.join(c * 2 for c in hex_val)
                return '#' + hex_val.lower()
    return None


def _get_style_colors(style_name: str) -> dict:
    """Build token->color map from a Pygments style."""
    from pygments.styles import get_style_by_name

    style = get_style_by_name(style_name)
    colors_map = {}
    for token_type, style_str in style.styles.items():
        color = _parse_color_from_style(style_str)
        if color:
            colors_map[token_type] = color
    return colors_map


_STYLE_CACHE: dict[str, dict] = {}


def _token_color(style_name: str, token_type) -> str:
    """Get hex color for token from Pygments style, walking parent chain."""
    if style_name not in _STYLE_CACHE:
        _STYLE_CACHE[style_name] = _get_style_colors(style_name)
    styles = _STYLE_CACHE[style_name]
    t = token_type
    while t is not None:
        if t in styles:
            return styles[t]
        t = getattr(t, 'parent', None)
    return '#000000'


class PDFBuilder(CourseBuilder):
    def __init__(
        self,
        output_path: Path | None = None,
        elements: list | None = None,
        theme: PDFTheme | None = None,
    ) -> None:
        self.elements = elements if elements is not None else []
        self.theme = theme or OceanTheme()
        self.doc = SimpleDocTemplate(str(output_path), pagesize=A4)

    def add_elements(self, elements: list) -> None:
        self.elements.extend(elements)

    def build(self) -> None:
        if self.doc:
            self.doc.build(
                self.elements,
                onFirstPage=self._draw_page_bg,
                onLaterPages=self._draw_page_bg,
            )

    def build_title(self, text: str) -> list:
        return [Paragraph(safe_text(text), self.theme.title), Spacer(1, 0.08 * inch)]

    def build_heading(self, text: str, anchor: str | None = None) -> list:
        content = (f'<a name="{html.escape(anchor)}"/>' if anchor else '') + safe_text(text)
        return [Paragraph(content, self.theme.heading), Spacer(1, 0.06 * inch)]

    def build_subheading(self, text: str, anchor: str | None = None) -> list:
        content = (f'<a name="{html.escape(anchor)}"/>' if anchor else '') + safe_text(text)
        return [Paragraph(content, self.theme.subheading), Spacer(1, 0.04 * inch)]

    def build_index_link(
        self,
        text: str,
        anchor: str,
        indent_pt: float = 0,
    ) -> list:
        m = re.match(r'^(\d+\.\d*\s+)(.*)$', (text or '').strip())
        if m:
            number, title = m.group(1), m.group(2)
            primary = self.theme._heading_color
            link = self.theme._link_color
            inner = (
                f'<font color="{html.escape(primary)}"><b>{safe_text(number.strip())}</b></font> '
                f'<a href="#{html.escape(anchor)}" color="{html.escape(link)}"><u>{safe_text(title)}</u></a>'
            )
        else:
            link = self.theme._link_color
            inner = (
                f'<a href="#{html.escape(anchor)}" color="{html.escape(link)}"><u>{safe_text(text)}</u></a>'
            )
        style = self.theme.normal
        if indent_pt > 0:
            style = ParagraphStyle(
                f'IndexIndent{int(indent_pt)}',
                parent=self.theme.normal,
                leftIndent=indent_pt,
            )
        return [Paragraph(inner, style)]

    def build_paragraph(self, text: str) -> list:
        return [Paragraph(safe_text(text), self.theme.normal)]

    def _token_to_color(self, token_type) -> str:
        """Map Pygments token type to hex color using Pygments style."""
        return _token_color(_DEFAULT_CODE_STYLE, token_type)

    def build_code_block(self, code: str, language: str | None = None) -> list:
        raw_code = (code or '').strip('\n\r\t')
        if not raw_code:
            return []

        raw_code = wrap_code_lines(raw_code, max_chars=70)
        lang = (language or 'text').strip().lower() or 'text'
        try:
            lexer = get_lexer_by_name(lang, stripall=False)
        except Exception:
            lexer = get_lexer_by_name('text', stripall=False)

        # Tokenize and build markup line-by-line so chunks never split inside a tag.
        line_markups: list[str] = []
        pieces: list[str] = []
        for _ttype, value in lex(raw_code, lexer):
            if not value:
                continue
            color = self._token_to_color(_ttype)
            parts = value.split('\n')
            for i, part in enumerate(parts):
                if i > 0:
                    line_markups.append(''.join(pieces))
                    pieces = []
                if part:
                    piece_escaped = html.escape(part).replace('{', '&#123;').replace('}', '&#125;')
                    pieces.append(f'<font color="{html.escape(color)}">{piece_escaped}</font>')

        if pieces:
            line_markups.append(''.join(pieces))
        code_style = ParagraphStyle(
            'CodeBlock',
            fontName=PDF_FONT_JETBRAINS,
            fontSize=9,
            leading=11,
        )
        _code_border_col = 9
        _code_content_col = MAX_CONTENT_WIDTH
        _code_bg = colors.HexColor('#EBEBEB')
        _code_border = colors.HexColor('#9E9E9E')
        _lines_per_page = 50
        rows = []
        for i in range(0, len(line_markups), _lines_per_page):
            chunk = '\n'.join(line_markups[i : i + _lines_per_page])
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
            link_para = Paragraph(link_tag(href, label), self.theme.normal)
            if content_flowables:
                content_flowables.append(Spacer(1, 0.08 * inch))
            content_flowables.append(link_para)
        if not content_flowables:
            return []

        _border_col = 9
        _content_col = MAX_CONTENT_WIDTH
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
            bulletColor=colors.HexColor(self.theme._heading_color),
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
                txt = f'<b>{html.escape(title)}</b>' if title_bold else safe_text(title)
                parts.append(Paragraph(txt, self.theme.normal))
            if content_flowables:
                parts.append(Spacer(1, 0.02 * inch))
                parts.extend(content_flowables)
            list_items.append(ListItem(parts))
        flow = ListFlowable(
            list_items,
            bulletType='bullet',
            bulletColor=colors.HexColor(self.theme._heading_color),
        )
        return [flow, Spacer(1, 0.1 * inch)]

    def build_numbered_list(self, items: list[str]) -> list:
        flow = ListFlowable(
            [ListItem(Paragraph(i, self.theme.normal)) for i in items],
            bulletType='1',
            bulletColor=colors.HexColor(self.theme._heading_color),
        )
        return [flow, Spacer(1, 0.1 * inch)]

    def build_numbered_list_with_content(self, items: list[list]) -> list:
        """Build numbered list where each item is a list of flowables."""
        list_items = [ListItem(flows) for flows in items if flows]
        if not list_items:
            return []
        flow = ListFlowable(
            list_items,
            bulletType='1',
            bulletColor=colors.HexColor(self.theme._heading_color),
        )
        return [flow, Spacer(1, 0.1 * inch)]

    def build_table(self, data: list[list[str]]) -> list:
        if not data:
            return []
        ncols = max(len(row) for row in data)
        if ncols == 0:
            return []
        _table_width = MAX_CONTENT_WIDTH
        _min_col = 30  # avoid negative availWidth when many columns
        col_width = max(_table_width / ncols, _min_col)
        col_widths = [col_width] * ncols
        _table_row_alt = colors.HexColor('#EBEBEB')

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
        max_w = width if width is not None else MAX_CONTENT_WIDTH
        max_h = MAX_IMAGE_HEIGHT

        img = Image(str(path), hAlign='CENTER')
        iw, ih = img.imageWidth, img.imageHeight
        if iw and ih:
            scale = min(1, max_w / iw, max_h / ih)
            img.drawWidth = iw * scale
            img.drawHeight = ih * scale

        # At wrap time, shrink further if frame is smaller (e.g. mid-page)
        def wrap(aW, aH):
            if img.drawWidth > aW or img.drawHeight > aH:
                img._restrictSize(aW, aH)
            return img.drawWidth, img.drawHeight

        img.wrap = wrap
        return [img, Spacer(1, 0.2 * inch)]

    def build_spacer(self, height: float = 0.2 * inch) -> list:
        return [Spacer(1, height)]

    def build_page_break(self) -> list:
        return [PageBreak()]

    def _draw_page_bg(self, canvas, _doc) -> None:
        canvas.saveState()
        canvas.setFillColor(self.theme.page_bg)
        canvas.rect(0, 0, self.doc.pagesize[0], self.doc.pagesize[1], fill=True, stroke=False)
        canvas.restoreState()
