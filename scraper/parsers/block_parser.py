from __future__ import annotations

from playwright.sync_api import Locator

from scraper.parsers.blocks import (
    CodeBlock,
    ImageWithButtonsBlock,
    LessonBlock,
    TextBlock,
    TitleBlock,
    UnknownBlock,
)


class BlockParser:
    def __init__(self, wrapper: Locator) -> None:
        self.wrapper = wrapper

    def _identify_block(self) -> type[LessonBlock]:
        # Code
        if (
            self.wrapper.locator('pre.block-text__code').count()
            or self.wrapper.locator('.block-text--code').count()
        ):
            return CodeBlock

        # Title/heading block
        if self.wrapper.locator('.block-text__heading').count():
            return TitleBlock

        # Rich text block
        if self.wrapper.locator('.fr-view').count():
            return TextBlock

        # Placeholder for widget blocks (not implemented yet)
        if self.wrapper.locator('.block-image').count() and self.wrapper.locator('button').count():
            return ImageWithButtonsBlock

        return UnknownBlock

    def parse_block(self, *, block_id: str | None) -> LessonBlock:
        block_cls = self._identify_block()
        return block_cls(block_id=block_id, locator=self.wrapper)
