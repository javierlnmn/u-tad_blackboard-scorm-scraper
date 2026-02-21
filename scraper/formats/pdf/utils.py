"""PDF helper utilities."""

from __future__ import annotations

import html


def safe_text(text: str) -> str:
    return html.escape(text or '', quote=True)


def wrap_code_lines(text: str, max_chars: int = 85) -> str:
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


def link_tag(href: str, link_text: str) -> str:
    safe_href = html.escape(href, quote=True)
    safe_label = html.escape(link_text, quote=True)
    return f'<a href="{safe_href}" color="#2563eb">{safe_label}</a>'


def html_inline_to_markup(node) -> str:
    from bs4 import NavigableString

    if isinstance(node, NavigableString):
        return html.escape(str(node))
    if not hasattr(node, 'name') or not node.name:
        return html.escape(str(node))

    name = node.name.lower()
    if name == 'br':
        return '<br/>'
    if name in {'strong', 'b'}:
        inner = ''.join(html_inline_to_markup(c) for c in node.contents)
        return f'<b>{inner}</b>' if inner.strip() else inner
    if name in {'em', 'i'}:
        inner = ''.join(html_inline_to_markup(c) for c in node.contents)
        return f'<i>{inner}</i>' if inner.strip() else inner
    if name == 'a':
        href = (node.get('href') or '').strip()
        label = ''.join(html_inline_to_markup(c) for c in node.contents).strip()
        label = label or node.get_text(' ', strip=True)
        if href:
            return link_tag(href, label or href)
        return html.escape(label)
    if name == 'code':
        inner = ''.join(html_inline_to_markup(c) for c in node.contents)
        return f'<font name="Courier">{html.escape(inner)}</font>'
    return ''.join(html_inline_to_markup(c) for c in node.contents)
