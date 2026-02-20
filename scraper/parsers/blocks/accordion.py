from __future__ import annotations

from dataclasses import dataclass, field

from scraper.formats.md import Markdown
from scraper.parsers.blocks.base import LessonBlock


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
            body_md = Markdown.html(body_html) or ''
            lines.append(Markdown.bullet_item(title, body_md))
        return '\n'.join(lines).strip()
