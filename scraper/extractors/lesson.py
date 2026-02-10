import logging

from playwright.sync_api import Frame, Page, TimeoutError

from scraper.models.course_scheme import CourseSchemeLesson
from scraper.models.lesson_content import LessonContent, LessonContentPart
from scraper.parsers.lesson import parse_lesson_content

logger = logging.getLogger(__name__)


def find_frame_with_matching_element(page: Page, selector: str) -> Frame | None:
    for frame in page.frames:
        try:
            if frame.locator(selector).count() > 0:
                return frame
        except Exception:
            continue
    return None


def extract_lesson(
    *,
    scorm_page: Page,
    scorm_frame: Frame,
    item: CourseSchemeLesson,
    total_items: int,
    sidebar_lesson_links_selector: str,
    lesson_content_selector: str,
    timeout_ms: int = 5000,
) -> tuple[Frame, LessonContent]:
    logger.info('Parsing lesson %s/%s: %s', item.index + 1, total_items, item.title)

    link = scorm_frame.locator(sidebar_lesson_links_selector).nth(item.index)
    link.click()

    try:
        scorm_frame.wait_for_selector(lesson_content_selector, state='visible', timeout=timeout_ms)
    except TimeoutError:
        logger.warning('Lesson content not found, refreshing frame...')

        refreshed = find_frame_with_matching_element(scorm_page, lesson_content_selector)
        if not refreshed:
            raise RuntimeError('Could not resolve SCORM content frame.')

        scorm_frame = refreshed
        logger.info('Refreshed SCORM content frame.')

        scorm_frame.wait_for_selector(lesson_content_selector, state='visible', timeout=timeout_ms)
        logger.info('Lesson content found after refresh.')

    lesson_el = scorm_frame.locator(lesson_content_selector).first
    parsed_contents: list[LessonContentPart] = parse_lesson_content(lesson_el)
    lesson = LessonContent(label=item.title, contents=parsed_contents)

    logger.info('Scraped %s/%s: %s', item.index + 1, total_items, item.title)
    return scorm_frame, lesson
