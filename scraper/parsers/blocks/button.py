from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown
from scraper.parsers.utils.md import render_link_callout


@dataclass
class ButtonBlock(LessonBlock):
    query_selector = '.blocks-button'

    href: str | None = None
    description_html: str = ''
    description_text: str = ''

    def _scrape(self) -> None:
        desc_fr = self.locator.locator('.blocks-button__description .fr-view').first
        self.description_html = desc_fr.inner_html() if desc_fr.count() else ''
        self.description_text = (desc_fr.text_content() or '').strip() if desc_fr.count() else ''

        button = self.locator.locator('a.blocks-button__button[href]').first
        self.href = (button.get_attribute('href') or '').strip() if button.count() else None
        if not self.href:
            self.href = None

        self.description_html = (self.description_html or '').strip()
        self.description_text = (self.description_text or '').strip() or (
            self.locator.text_content() or ''
        ).strip()

    def _render_md(self, *, assets_dir=None) -> str:
        desc_md = html_fragment_to_markdown(self.description_html or '').strip()
        body = desc_md or (self.description_text or '')

        return render_link_callout(body, self.href)

    def _render_txt(self, *, assets_dir=None) -> str:
        body = (self.description_text or '').strip()
        if self.href:
            if body:
                return f'{body}\n{self.href}'.strip()
            return self.href
        return body
