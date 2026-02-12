from playwright.sync_api import Locator

from scraper.parsers.block_parser import BlockParser
from scraper.parsers.blocks import LessonBlock


def parse_lesson_content(lesson_el: Locator) -> list[LessonBlock]:
    blocks = lesson_el.locator('section.blocks-lesson > div.noOutline[data-block-id]')
    if not blocks.count():
        blocks = lesson_el.locator('section.blocks-lesson div.noOutline[data-block-id]')

    parts: list[LessonBlock] = []
    for i in range(blocks.count()):
        wrapper = blocks.nth(i)
        block_id = wrapper.get_attribute('data-block-id')

        block_scraper = BlockParser(wrapper)
        block = block_scraper.parse_block(block_id=block_id)

        parts.append(block)

    return parts
