from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from scraper.parsers.blocks.base import LessonBlock


@dataclass()
class TextBlock(LessonBlock):
    query_selector = '.fr-view'

    def _scrape(self) -> None:
        fr = self.locator.locator('.fr-view').first
        if fr.count():
            html = fr.inner_html()
            text = fr.inner_text()
        else:
            html = self.locator.inner_html()
            text = self.locator.inner_text()

        plain = (text or '').strip()
        self.plain_text = plain

        md = _html_fragment_to_markdown(html)
        self.markdown = md.strip() if md.strip() else plain

    def render(self, format: str = 'md') -> str:
        return super().render(format)


def _html_fragment_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html or '', 'html.parser')
    parts: list[str] = []

    for child in soup.contents:
        out = _render_node_as_blocks(child)
        if out:
            parts.extend(out)

    return _join_blocks(parts)


def _render_node_as_blocks(node) -> list[str]:
    if isinstance(node, NavigableString):
        text = str(node).strip()
        return [text] if text else []

    if not isinstance(node, Tag):
        return []

    name = node.name.lower()

    if name == 'p':
        txt = _render_inline(node).strip()
        return [txt] if txt else []

    if name in {'ul', 'ol'}:
        return _render_list(node)

    if name == 'table':
        md = _render_table(node)
        return [md] if md else []

    if name == 'pre':
        code = node.get_text('\n', strip=False).rstrip('\n')
        if not code.strip():
            return []
        return [f'```\n{code}\n```']

    # Containers/wrappers: recurse into children as blocks.
    if name in {'div', 'section', 'article', 'span'}:
        parts: list[str] = []
        for child in node.contents:
            parts.extend(_render_node_as_blocks(child))
        return parts

    # Default: treat unknown tags as inline text.
    txt = _render_inline(node).strip()
    return [txt] if txt else []


def _render_inline(node) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ''

    name = node.name.lower()

    if name == 'br':
        return '\n'

    if name in {'strong', 'b'}:
        inner = _render_inline_children(node).strip()
        return f'**{inner}**' if inner else ''

    if name in {'em', 'i'}:
        inner = _render_inline_children(node).strip()
        return f'*{inner}*' if inner else ''

    if name == 'code':
        inner = _render_inline_children(node).strip().replace('`', r'\`')
        return f'`{inner}`' if inner else ''

    if name == 'a':
        label = _render_inline_children(node).strip() or node.get_text(' ', strip=True)
        href = (node.get('href') or '').strip()
        if href:
            return f'[{label}]({href})'
        return label

    # If a block tag appears inline, flatten to text.
    if name in {'p', 'li'}:
        return _render_inline_children(node)

    return _render_inline_children(node)


def _render_inline_children(tag: Tag) -> str:
    pieces = [_render_inline(child) for child in tag.contents]
    out: list[str] = []

    for piece in pieces:
        if not piece:
            continue

        if out:
            prev = out[-1]
            if prev.endswith('**') and piece[:1] and not piece[:1].isspace() and piece[:1].isalnum():
                out[-1] = prev + ' '

        out.append(piece)

    return ''.join(out)


def _render_list(list_tag: Tag, *, indent: int = 0) -> list[str]:
    ordered = list_tag.name.lower() == 'ol'
    items: list[str] = []
    i = 1

    for li in list_tag.find_all('li', recursive=False):
        bullet = f'{i}.' if ordered else '-'
        i += 1

        # Render the LI's direct content (excluding nested lists which we render separately).
        chunks: list[str] = []
        for child in li.contents:
            if isinstance(child, Tag) and child.name and child.name.lower() in {'ul', 'ol'}:
                continue
            chunks.append(_render_inline(child))
        line = ' '.join(''.join(chunks).split())
        prefix = ('  ' * indent) + f'{bullet} '
        if line.strip():
            items.append(prefix + line.strip())

        # Nested lists inside this li
        for nested in li.find_all(['ul', 'ol'], recursive=False):
            items.extend(_render_list(nested, indent=indent + 1))

    return items


def _render_table(table: Tag) -> str:
    rows = table.find_all('tr')
    if not rows:
        return ''

    def cell_text(cell: Tag) -> str:
        txt = cell.get_text(' ', strip=True)
        return txt.replace('|', r'\|')

    parsed_rows: list[list[str]] = []
    for r in rows:
        cells = r.find_all(['th', 'td'], recursive=False)
        if not cells:
            # Some tables wrap cells deeper; fallback to any th/td.
            cells = r.find_all(['th', 'td'])
        parsed_rows.append([cell_text(c) for c in cells])

    col_count = max((len(r) for r in parsed_rows), default=0)
    if col_count == 0:
        return ''

    for r in parsed_rows:
        r.extend([''] * (col_count - len(r)))

    header = parsed_rows[0]
    body = parsed_rows[1:]

    def fmt_row(r: list[str]) -> str:
        return '| ' + ' | '.join(r) + ' |'

    lines = [fmt_row(header), '| ' + ' | '.join(['---'] * col_count) + ' |']
    lines.extend(fmt_row(r) for r in body)
    return '\n'.join(lines)


def _join_blocks(blocks: list[str]) -> str:
    cleaned = [b.strip() for b in blocks if b and b.strip()]
    return '\n\n'.join(cleaned)
