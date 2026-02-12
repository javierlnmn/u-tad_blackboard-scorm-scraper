from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown


@dataclass
class TextBlock(LessonBlock):
    query_selector = '.block-text .fr-view'

    def _scrape(self) -> None:
        fr = self.locator.locator('.block-text .fr-view').first
        if fr.count():
            html = fr.inner_html()
            text = fr.inner_text()
        else:
            html = self.locator.inner_html()
            text = self.locator.inner_text()

        plain = (text or '').strip()
        self.plain_text = plain

        md = html_fragment_to_markdown(html)
        self.markdown = md.strip() if md.strip() else plain

    def render(self, format: str = 'md', *, assets_dir=None) -> str:
        return super().render(format, assets_dir=assets_dir)
