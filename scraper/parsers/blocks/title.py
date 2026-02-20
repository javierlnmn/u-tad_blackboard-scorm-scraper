from __future__ import annotations

from dataclasses import dataclass

from scraper.formats.md import Markdown
from scraper.parsers.blocks.base import LessonBlock


@dataclass
class TitleBlock(LessonBlock):
    query_selector = '.block-text__heading'

    level: int | None = None
    title: str = ''

    def _scrape(self) -> None:
        heading = self.locator.locator('.block-text__heading').first
        level = None
        for i in range(1, 7):
            if heading.locator(f'h{i}').count():
                level = i
                break
        text = heading.inner_text() if heading.count() else self.locator.inner_text()
        self.title = (text or '').strip()
        self.level = level

    def _render_md(self, *, assets_dir=None) -> str:
        source_level = self.level or 3
        h = min(max(source_level + 1, 4), 6)
        return Markdown.heading(h, self.title)

    def _render_pdf(self, builder, *, assets_dir=None) -> list:
        return builder.build_subheading(self.title) if self.title else []
