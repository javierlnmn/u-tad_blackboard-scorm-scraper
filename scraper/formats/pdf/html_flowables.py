from __future__ import annotations

import html
from pathlib import Path

from bs4 import BeautifulSoup
from reportlab.platypus import Paragraph

from .builder import PDFBuilder
from .utils import html_inline_to_markup


def html_to_flowables(
    html_text: str,
    builder: PDFBuilder,
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
        return html_inline_to_markup(node)

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
