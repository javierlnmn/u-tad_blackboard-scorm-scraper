from playwright.sync_api import Locator

from scraper.models.lesson_content import LessonContentPart


def parse_lesson_content(lesson_el: Locator) -> list[LessonContentPart]:
    pass
