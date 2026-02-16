from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown


@dataclass
class AccordionBlock(LessonBlock):
    query_selector = '.blocks-accordion'

    items: list[tuple[str, str]] = field(default_factory=list)  # (title, md_body)

    def _scrape(self) -> None:
        items: list[tuple[str, str]] = []

        accordion_items = self.locator.locator('.blocks-accordion__item')
        for i in range(accordion_items.count()):
            item = accordion_items.nth(i)

            title_fr = item.locator('.blocks-accordion__title .fr-view').first
            title = (title_fr.text_content() or '').strip() if title_fr.count() else ''
            title = ' '.join(title.split())
            if not title:
                continue

            desc_fr = item.locator('.blocks-accordion__description .fr-view').first
            desc_html = desc_fr.inner_html() if desc_fr.count() else ''
            desc_md = html_fragment_to_markdown(desc_html).strip()
            if not desc_md and desc_fr.count():
                desc_md = (desc_fr.text_content() or '').strip()

            items.append((title, desc_md))

        self.items = items
        self.plain_text = (
            ', '.join(t for t, _ in items) if items else (self.locator.text_content() or '').strip()
        )
        self.markdown = _render_accordion_md(items)

    def render(self, format: str = 'md', *, assets_dir=None) -> str:
        return super().render(format, assets_dir=assets_dir)


def _render_accordion_md(items: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    for title, body in items:
        lines.append(f'- **{title}**  ')
        if body:
            for ln in body.splitlines():
                lines.append(('  ' + ln) if ln.strip() else '')
    return '\n'.join(lines).strip()
