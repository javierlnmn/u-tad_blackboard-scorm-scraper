from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks.base import LessonBlock


@dataclass()
class UnknownBlock(LessonBlock):
    # No selector: this is only used as the fallback.

    def _scrape(self) -> None:
        plain = (self.locator.inner_text() or '').strip()
        self.plain_text = plain
        self.markdown = plain

    def render(self, format: str = 'md') -> str:
        return super().render(format)
