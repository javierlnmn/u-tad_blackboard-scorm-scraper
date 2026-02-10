from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks import LessonBlock


@dataclass(slots=True)
class CodeBlock(LessonBlock):
    def _parse(self) -> None:
        pre = self.locator.locator('pre.block-text__code').first
        code = pre.inner_text() if pre.count() else self.locator.inner_text()
        code = (code or '').rstrip('\n')
        self.plain_text = code
        self.markdown = f'```\n{code}\n```'

    def render(self, format: str = 'md') -> str:
        return super().render(format)
