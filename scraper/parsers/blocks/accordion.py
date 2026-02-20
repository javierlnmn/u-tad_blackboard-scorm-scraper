from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock
from scraper.utils.html_to_markdown import html_fragment_to_markdown


@dataclass
class AccordionBlock(LessonBlock):
    query_selector = '.blocks-accordion'

    items: list[tuple[str, str]] = field(default_factory=list)  # (title, body_html)

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
            items.append((title, (desc_html or '').strip()))

        self.items = items

    def _render_md(self, *, assets_dir=None) -> str:
        if not self.items:
            return (self.locator.text_content() or '').strip()

        lines: list[str] = []
        for title, body_html in self.items:
            body_md = html_fragment_to_markdown(body_html or '').strip()
            if not body_md:
                body_md = ''

            lines.append(f'- **{title}**  ')
            if body_md:
                for ln in body_md.splitlines():
                    lines.append(('  ' + ln) if ln.strip() else '')
        return '\n'.join(lines).strip()

    def _render_txt(self, *, assets_dir=None) -> str:
        if not self.items:
            return (self.locator.text_content() or '').strip()

        parts: list[str] = []
        for title, body_html in self.items:
            body = html_fragment_to_markdown(body_html or '').strip()
            chunk = title
            if body:
                chunk = f'{chunk}\n{body}'.strip()
            parts.append(chunk)
        return '\n\n'.join(parts).strip()
