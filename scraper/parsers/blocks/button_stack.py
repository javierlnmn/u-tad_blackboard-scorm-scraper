from __future__ import annotations

from dataclasses import dataclass, field

from scraper.formats.md import Markdown
from scraper.parsers.blocks.base import LessonBlock


@dataclass
class ButtonStackBlock(LessonBlock):
    query_selector = '.blocks-buttonstack'

    entries: list[tuple[str, str | None]] = field(default_factory=list)  # (desc_html, href)

    def _scrape(self) -> None:
        containers = self.locator.locator(f'{self.query_selector} .blocks-button__container')

        entries: list[tuple[str, str | None]] = []
        for i in range(containers.count()):
            container = containers.nth(i)

            desc_fr = container.locator('.blocks-button__description .fr-view').first
            desc_html = desc_fr.inner_html() if desc_fr.count() else ''

            button = container.locator('a.blocks-button__button[href]').first
            href = (button.get_attribute('href') or '').strip() if button.count() else None
            if not href:
                href = None

            if not desc_html.strip() and not href:
                continue

            entries.append((desc_html.strip(), href))

        self.entries = entries

    def _render_md(self, *, assets_dir=None) -> str:
        if not self.entries:
            return (self.locator.text_content() or '').strip()

        callouts: list[str] = []
        for desc_html, href in self.entries:
            desc_md = Markdown.html(desc_html)
            callouts.append(Markdown.link_callout(desc_md, href))
        return '\n\n'.join(c for c in callouts if c.strip()).strip()

    def _render_pdf(self, builder, *, assets_dir=None) -> list:
        if not self.entries:
            return []
        out: list = []
        for desc_html, href in self.entries:
            body = Markdown.html(desc_html) or ''
            if body or href:
                out.extend(builder.build_callout(body, href, link_text='View link'))
        return out
