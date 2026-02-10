import logging

from playwright.sync_api import Frame, Page

from scraper.extractors.lesson import extract_lesson, find_frame_with_matching_element
from scraper.models.lesson_content import LessonContent
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
        scorm_frame = find_frame_with_matching_element(scorm_page, SIDEBAR_SELECTOR)

    if not scorm_frame:
        scorm_frame = find_frame_with_matching_element(scorm_page, LESSON_CONTENT_SELECTOR)

    if not scorm_frame:
        raise RuntimeError('Could not resolve SCORM content frame.')
    else:
        logger.info('Resolved SCORM content frame.')

    logger.info('Parsing sidebar...')
    sidebar = scorm_frame.locator(SIDEBAR_SELECTOR)
    sidebar.wait_for(state='visible')
    sidebar_html = sidebar.inner_html()
    wrapped = f'<div id="nav-content-sidebar">{sidebar_html}</div>'
    course_scheme = parse_sidebar(wrapped)

    if not course_scheme:
        logger.warning('No course scheme sections/lessons found.')
        return []
    else:
        total_items = sum(len(s.lessons) for s in course_scheme)
        logger.info(
            'Found %s course scheme sections with %s total lessons.',
            len(course_scheme),
            total_items,
        )

    lessons: list[LessonContent] = []

    lesson_refs = [lesson for section in course_scheme for lesson in section.lessons]
    for lesson_ref in lesson_refs:
        scorm_frame, lesson = extract_lesson(
            scorm_page=scorm_page,
            scorm_frame=scorm_frame,
            item=lesson_ref,
            total_items=len(lesson_refs),
            sidebar_lesson_links_selector=SIDEBAR_LESSON_LINKS_SELECTOR,
            lesson_content_selector=LESSON_CONTENT_SELECTOR,
            timeout_ms=5000,
        )
        lessons.append(lesson)

    return lessons
