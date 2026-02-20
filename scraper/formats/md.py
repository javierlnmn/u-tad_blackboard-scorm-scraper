from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


class Markdown:
    """Structured markdown rendering helpers."""

    @staticmethod
    def html(html: str) -> str:
        """Convert an HTML fragment to markdown. Returns stripped string."""
        return Markdown._html_to_markdown(html or '').strip()

    @staticmethod
    def heading(level: int, text: str) -> str:
        """Render a markdown heading (e.g. #### Title). Level 1–6."""
        h = min(max(level, 1), 6)
        return f'{"#" * h} {text}'.strip()

    @staticmethod
    def numbered_item(num: str, body: str) -> str:
        """Render a numbered list item with hanging indent (for steps, etc.)."""
        prefix = f'{num}. '
        lines = body.splitlines() if body else ['']
        if not lines:
            return prefix.rstrip()
        out = [prefix + lines[0].strip()]
        indent = ' ' * len(prefix)
        for ln in lines[1:]:
            out.append((indent + ln) if ln.strip() else '')
        return '\n'.join(out).rstrip()

    @staticmethod
    def bullet_item(title: str, body: str) -> str:
        """Render a bullet with **bold title** and indented body (accordion, tabs, etc.)."""
        lines: list[str] = [f'- **{title}**  ']
        if body:
            for ln in body.splitlines():
                lines.append(('  ' + ln) if ln.strip() else '')
        return '\n'.join(lines).rstrip()

    @staticmethod
    def bullet_list(items: list[str]) -> str:
        """Render a simple unordered list: - item1, - item2, ..."""
        return '\n'.join(f'- {s.strip()}' for s in items if s and s.strip()).strip()

    @staticmethod
    def numbered_list(items: list[str]) -> str:
        """Render a simple ordered list: 1. item1, 2. item2, ..."""
        lines: list[str] = []
        for i, s in enumerate((s for s in items if s and s.strip()), start=1):
            lines.append(f'{i}. {s.strip()}')
        return '\n'.join(lines).strip()

    @staticmethod
    def link_callout(body: str, href: str | None) -> str:
        """Render a blockquote-style callout with optional link."""
        lines: list[str] = []
        body = (body or '').strip()
        if body:
            for ln in body.splitlines():
                lines.append(f'> {ln}'.rstrip())
        if href:
            if lines:
                lines.append('>')
            lines.append(f'> [Link]({href})')
        return '\n'.join(lines).strip()

    @staticmethod
    def image(alt: str, path: str) -> str:
        """Render a markdown image."""
        return f'![{alt or "image"}]({path})'

    @staticmethod
    def code_block(code: str, lang: str | None = None) -> str:
        """Render a fenced code block."""
        fence = f'```{lang}' if lang else '```'
        return f'{fence}\n{code}\n```'

    @staticmethod
    def table(headers: list[str], rows: list[list[str]]) -> str:
        """Render a markdown table from headers and row data."""
        col_count = max(len(headers), max((len(r) for r in rows), default=0))
        if col_count == 0:
            return ''
        h = headers + [''] * (col_count - len(headers))

        def fmt_row(r: list[str]) -> str:
            row = r + [''] * (col_count - len(r))
            return '| ' + ' | '.join(c.replace('|', r'\|') for c in row) + ' |'

        lines = [fmt_row(h), '| ' + ' | '.join(['---'] * col_count) + ' |']
        lines.extend(fmt_row(r) for r in rows)
        return '\n'.join(lines)

    @staticmethod
    def _html_to_markdown(html: str) -> str:
        soup = BeautifulSoup(html or '', 'html.parser')
        parts: list[str] = []
        for child in soup.contents:
            out = Markdown._render_node_as_blocks(child)
            if out:
                parts.extend(out)
        return Markdown._join_blocks(parts)

    @staticmethod
    def _render_node_as_blocks(node) -> list[str]:
        if isinstance(node, NavigableString):
            text = str(node).strip()
            return [text] if text else []

        if not isinstance(node, Tag):
            return []

        name = node.name.lower()

        if name == 'p':
            txt = Markdown._render_inline(node).strip()
            return [txt] if txt else []

        if name in {'ul', 'ol'}:
            return Markdown._render_html_list(node)

        if name == 'table':
            md = Markdown._render_html_table(node)
            return [md] if md else []

        if name == 'pre':
            code = node.get_text('\n', strip=False).rstrip('\n')
            if not code.strip():
                return []
            return [f'```\n{code}\n```']

        if name in {'div', 'section', 'article', 'span'}:
            parts: list[str] = []
            for child in node.contents:
                parts.extend(Markdown._render_node_as_blocks(child))
            return parts

        txt = Markdown._render_inline(node).strip()
        return [txt] if txt else []

    @staticmethod
    def _render_inline(node) -> str:
        if isinstance(node, NavigableString):
            return str(node)
        if not isinstance(node, Tag):
            return ''

        name = node.name.lower()

        if name == 'br':
            return '\n'

        if name in {'strong', 'b'}:
            inner = Markdown._render_inline_children(node).strip()
            return f'**{inner}**' if inner else ''

        if name in {'em', 'i'}:
            inner = Markdown._render_inline_children(node).strip()
            return f'*{inner}*' if inner else ''

        if name == 'code':
            inner = Markdown._render_inline_children(node).strip().replace('`', r'\`')
            return f'`{inner}`' if inner else ''

        if name == 'a':
            label = Markdown._render_inline_children(node).strip() or node.get_text(' ', strip=True)
            href = (node.get('href') or '').strip()
            if href:
                return f'[{label}]({href})'
            return label

        if name in {'p', 'li'}:
            return Markdown._render_inline_children(node)

        return Markdown._render_inline_children(node)

    @staticmethod
    def _render_inline_children(tag: Tag) -> str:
        pieces = [Markdown._render_inline(child) for child in tag.contents]
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

    @staticmethod
    def _render_html_list(list_tag: Tag, *, indent: int = 0) -> list[str]:
        """Convert HTML <ul> or <ol> to markdown (simple bullet/numbered list)."""
        ordered = list_tag.name.lower() == 'ol'
        items: list[str] = []
        i = 1

        for li in list_tag.find_all('li', recursive=False):
            bullet = f'{i}.' if ordered else '-'
            i += 1

            chunks: list[str] = []
            for child in li.contents:
                if isinstance(child, Tag) and child.name and child.name.lower() in {'ul', 'ol'}:
                    continue
                chunks.append(Markdown._render_inline(child))
            line = ' '.join(''.join(chunks).split())
            prefix = ('  ' * indent) + f'{bullet} '
            if line.strip():
                items.append(prefix + line.strip())

            for nested in li.find_all(['ul', 'ol'], recursive=False):
                items.extend(Markdown._render_html_list(nested, indent=indent + 1))

        return ['\n'.join(items).rstrip()] if items else []

    @staticmethod
    def _render_html_table(table: Tag) -> str:
        rows = table.find_all('tr')
        if not rows:
            return ''

        def cell_text(cell: Tag) -> str:
            txt = cell.get_text(' ', strip=True)
            return txt.replace('|', r'\|')

        parsed_rows: list[list[str]] = []
        for r in rows:
            cells = r.find_all(['th', 'td'], recursive=False) or r.find_all(['th', 'td'])
            parsed_rows.append([cell_text(c) for c in cells])

        col_count = max((len(r) for r in parsed_rows), default=0)
        if col_count == 0:
            return ''

        for r in parsed_rows:
            r.extend([''] * (col_count - len(r)))

        header = parsed_rows[0]
        body = parsed_rows[1:]
        return Markdown.table(header, body)

    @staticmethod
    def _join_blocks(blocks: list[str]) -> str:
        cleaned = [b.strip() for b in blocks if b and b.strip()]
        return '\n\n'.join(cleaned)
