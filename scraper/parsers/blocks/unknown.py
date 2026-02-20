from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks.base import LessonBlock


@dataclass()
class UnknownBlock(LessonBlock):
    # Used as the fallback.

    text: str = ''

    def _scrape(self) -> None:
        self.text = (self.locator.inner_text() or '').strip()

    def _render_md(self, *, assets_dir=None) -> str:
        return self.text

    def _render_pdf(self, builder, *, assets_dir=None) -> list:
        return builder.build_paragraph(self.text) if self.text else []
