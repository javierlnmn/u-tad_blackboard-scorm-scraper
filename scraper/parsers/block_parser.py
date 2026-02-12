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
        for block_cls in (CodeBlock, TitleBlock, TextBlock, ImageWithButtonsBlock):
            selector = getattr(block_cls, 'query_selector', '') or ''
            if selector and self.wrapper.locator(selector).count():
                return block_cls

        return UnknownBlock

    def parse_block(self, *, block_id: str | None) -> LessonBlock:
        block_cls = self._identify_block()
        return block_cls(block_id=block_id, locator=self.wrapper)
