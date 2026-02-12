from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks import LessonBlock


@dataclass(slots=True)
class ImageWithButtonsBlock(LessonBlock):
    query_selector = '.block-image button, .block-image [role="button"]'

    def _scrape(self) -> None:
        # TODO: implement real widget parsing; for now keep a plain-text fallback.
        plain = (self.locator.inner_text() or '').strip()
        self.plain_text = plain
        self.markdown = plain

    def render(self, format: str = 'md') -> str:
        return super().render(format)
