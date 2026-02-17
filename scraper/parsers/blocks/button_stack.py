from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown
from scraper.parsers.utils.md import render_link_callout


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
            desc_md = html_fragment_to_markdown(desc_html or '').strip()
            callouts.append(render_link_callout(desc_md, href))
        return '\n\n'.join(c for c in callouts if c.strip()).strip()

    def _render_txt(self, *, assets_dir=None) -> str:
        if not self.entries:
            return (self.locator.text_content() or '').strip()

        parts: list[str] = []
        for desc_html, href in self.entries:
            desc_txt = html_fragment_to_markdown(desc_html or '').strip()
            chunk = desc_txt
            if href:
                chunk = f'{chunk}\n{href}'.strip() if chunk else href
            if chunk:
                parts.append(chunk)
        return '\n\n'.join(parts).strip()
