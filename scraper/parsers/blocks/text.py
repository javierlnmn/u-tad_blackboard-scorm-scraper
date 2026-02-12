from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks import LessonBlock


@dataclass(slots=True)
class TextBlock(LessonBlock):
    query_selector = '.fr-view'

    def _scrape(self) -> None:
        fr = self.locator.locator('.fr-view').first
        text = fr.inner_text() if fr.count() else self.locator.inner_text()
        plain = (text or '').strip()
        self.plain_text = plain
        # TODO: HTML->Markdown conversion (tables/lists) later; for now markdown == plain text.
        self.markdown = plain

    def render(self, format: str = 'md') -> str:
        return super().render(format)
