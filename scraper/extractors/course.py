import logging

from playwright.sync_api import Frame, Page

from scraper.extractors.lesson import extract_lesson, find_frame_with_visible_locator
from scraper.models import LessonContent
from scraper.parsers.sidebar import SIDEBAR_LESSON_LINKS_SELECTOR, parse_sidebar

logger = logging.getLogger(__name__)

CONTENT_FRAME = '#content-frame'
LESSON_CONTENT_SELECTOR = '[data-lesson-id]'
SIDEBAR_SELECTOR = '#nav-content-sidebar'


def _frame_from_iframe(page: Page, iframe_query_selector: str) -> Frame | None:
    iframe = page.query_selector(iframe_query_selector)
    if not iframe:
        return None
    return iframe.content_frame()


def extract_course(scorm_page: Page) -> list[LessonContent]:

    scorm_frame: Frame | None = _frame_from_iframe(scorm_page, f'iframe{CONTENT_FRAME}')

    if not scorm_frame:
        scorm_frame = _frame_from_iframe(scorm_page, 'iframe')

    if not scorm_frame:
        scorm_frame = find_frame_with_visible_locator(scorm_page, SIDEBAR_SELECTOR)

    if not scorm_frame:
        scorm_frame = find_frame_with_visible_locator(scorm_page, LESSON_CONTENT_SELECTOR)

    if not scorm_frame:
        raise RuntimeError('Could not resolve SCORM content frame.')
    else:
        logger.info('Resolved SCORM content frame.')

    logger.info('Parsing sidebar...')
    sidebar = scorm_frame.locator(SIDEBAR_SELECTOR)
    sidebar.wait_for(state='visible')
    sidebar_html = sidebar.inner_html()
    wrapped = f'<div id="nav-content-sidebar">{sidebar_html}</div>'
    items = parse_sidebar(wrapped)

    if not items:
        logger.warning('No sidebar items found.')
        return []
    else:
        logger.info('Found %s sidebar items.', len(items))

    lessons: list[LessonContent] = []

    for item in items:
        scorm_frame, lesson = extract_lesson(
            scorm_page=scorm_page,
            scorm_frame=scorm_frame,
            item=item,
            total_items=len(items),
            sidebar_lesson_links_selector=SIDEBAR_LESSON_LINKS_SELECTOR,
            lesson_content_selector=LESSON_CONTENT_SELECTOR,
            timeout_ms=5000,
        )
        lessons.append(lesson)

    return lessons
