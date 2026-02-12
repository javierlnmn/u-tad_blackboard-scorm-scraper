from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks import LessonBlock


@dataclass(slots=True)
class TitleBlock(LessonBlock):
    query_selector = '.block-text__heading'

    level: int | None = None

    def _scrape(self) -> None:
        heading = self.locator.locator('.block-text__heading').first
        level = None
        for i in range(1, 7):
            if heading.locator(f'h{i}').count():
                level = i
                break
        text = heading.inner_text() if heading.count() else self.locator.inner_text()
        title = (text or '').strip()
        h = min(max(level or 3, 1), 6)
        self.level = level
        self.plain_text = title
        self.markdown = f'{"#" * h} {title}'.strip()

    def render(self, format: str = 'md') -> str:
        return super().render(format)
