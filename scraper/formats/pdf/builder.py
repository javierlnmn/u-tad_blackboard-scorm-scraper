"""PDFBuilder for constructing PDF documents."""

from __future__ import annotations

import html
from pathlib import Path

from bs4 import BeautifulSoup
from pygments import highlight
from pygments.formatters import HtmlFormatter
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

from .config import MAX_CONTENT_WIDTH
from .themes import OceanTheme, PDFTheme
from .utils import link_tag, safe_text, wrap_code_lines


class PDFBuilder:
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
        self.elements.extend(flowables)

    def build_title(self, text: str) -> list:
        return [Paragraph(safe_text(text), self.theme.title), Spacer(1, 0.08 * inch)]

    def build_heading(self, text: str) -> list:
        return [Paragraph(safe_text(text), self.theme.heading), Spacer(1, 0.06 * inch)]

    def build_subheading(self, text: str) -> list:
        return [Paragraph(safe_text(text), self.theme.subheading), Spacer(1, 0.04 * inch)]

    def build_paragraph(self, text: str) -> list:
        return [Paragraph(safe_text(text), self.theme.normal)]

    def build_code_block(self, code: str, language: str | None = None) -> list:
        raw_code = (code or '').strip()
        if not raw_code:
            return []

        raw_code = wrap_code_lines(raw_code, max_chars=85)
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
        _code_content_col = MAX_CONTENT_WIDTH
        _code_bg = colors.HexColor('#EBEBEB')
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
            link_para = Paragraph(link_tag(href, label), self.theme.normal)
            if content_flowables:
                content_flowables.append(Spacer(1, 0.08 * inch))
            content_flowables.append(link_para)
        if not content_flowables:
            return []

        _border_col = 12
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
        _table_width = MAX_CONTENT_WIDTH
        col_widths = [_table_width / ncols] * ncols
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
        img = Image(str(path), hAlign='CENTER')
        w = width if width is not None else MAX_CONTENT_WIDTH
        img.drawWidth = min(w, img.imageWidth)
        img.drawHeight = img.drawWidth * img.imageHeight / img.imageWidth
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

    def build(self) -> None:
        if self.doc:
            self.doc.build(
                self.elements,
                onFirstPage=self._draw_page_bg,
                onLaterPages=self._draw_page_bg,
            )
