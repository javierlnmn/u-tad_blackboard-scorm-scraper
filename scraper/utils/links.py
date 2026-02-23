from __future__ import annotations


def slugify(text: str) -> str:
    s = (text or '').strip().lower()
    out: list[str] = []
    prev_dash = False
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif ch in {' ', '-'}:
            if not prev_dash:
                out.append('-')
                prev_dash = True
    return ''.join(out).strip('-') or 'placeholder-slug'
