from __future__ import annotations

from dataclasses import dataclass

from scraper.formats.md import Markdown
from scraper.parsers.blocks.base import LessonBlock


@dataclass
class TextBlock(LessonBlock):
    query_selector = '.block-text .fr-view'

    html: str = ''
    text: str = ''

    def _scrape(self) -> None:
        fr = self.locator.locator('.block-text .fr-view').first
        if fr.count():
            self.html = fr.inner_html() or ''
            self.text = fr.inner_text() or ''
        else:
            self.html = self.locator.inner_html() or ''
            self.text = self.locator.inner_text() or ''

        self.html = (self.html or '').strip()
        self.text = (self.text or '').strip()

    def _render_md(self, *, assets_dir=None) -> str:
        md = Markdown.html(self.html)
        return md if md else (self.text or '')
