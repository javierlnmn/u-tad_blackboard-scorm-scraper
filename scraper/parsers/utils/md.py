from __future__ import annotations


def render_link_callout(body: str, href: str | None) -> str:
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
