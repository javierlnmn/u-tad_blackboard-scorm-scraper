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
