from __future__ import annotations

import logging

from playwright.sync_api import Frame, Locator, Page

from scraper.extractors.lesson import extract_lesson
from scraper.models.course_scheme import CourseScheme, CourseSchemeSection
from scraper.parsers.sidebar import SIDEBAR_LESSON_LINKS_SELECTOR, parse_sidebar

logger = logging.getLogger(__name__)

CONTENT_FRAME = '#content-frame'
COVER_PAGE_SELECTOR = '#cover'
COVER_START_COURSE_BUTTON_SELECTOR = '.cover__header-content-action-link'
LESSON_CONTENT_SELECTOR = '[data-lesson-id]'
SIDEBAR_SELECTOR = '#nav-content-sidebar'


def _frame_from_iframe(page: Page, iframe_query_selector: str) -> Frame | None:
    iframe = page.query_selector(iframe_query_selector)
    if not iframe:
        return None
    return iframe.content_frame()


def _get_course_scheme(scorm_frame: Locator) -> list[CourseSchemeSection]:
    sidebar = scorm_frame.locator(SIDEBAR_SELECTOR)
    sidebar.wait_for(state='visible')
    sidebar_html = sidebar.inner_html()
    wrapped = f'<div id="nav-content-sidebar">{sidebar_html}</div>'
    course_scheme = parse_sidebar(wrapped)
    return course_scheme


def extract_course(scorm_page: Page) -> CourseScheme:

    scorm_frame: Frame | None = _frame_from_iframe(scorm_page, f'iframe{CONTENT_FRAME}')

    if not scorm_frame:
        scorm_frame = _frame_from_iframe(scorm_page, 'iframe')

    if not scorm_frame:
        raise RuntimeError('Could not resolve SCORM content frame.')
    else:
        logger.info('Resolved SCORM content frame.')

    if scorm_frame.locator(f'div{COVER_PAGE_SELECTOR}').count() > 0:
        start_course_button = scorm_frame.locator(f'a{COVER_START_COURSE_BUTTON_SELECTOR}')
        start_course_button.click()

    logger.info('Parsing course scheme...')
    course_scheme = _get_course_scheme(scorm_frame)

    if not course_scheme:
        logger.warning('No course scheme sections/lessons found.')
        return CourseScheme(title=(scorm_page.title() or 'Course').strip(), sections=[])
    else:
        total_items = sum(len(s.lessons) for s in course_scheme)
        logger.info(
            'Found %s course scheme sections with %s total lessons.',
            len(course_scheme),
            total_items,
        )

    course_title = (scorm_page.title() or 'Course').strip()

    flat_lessons = [lesson for section in course_scheme for lesson in section.lessons]
    total_lessons = len(flat_lessons)

    for section in course_scheme:
        for lesson_ref in section.lessons:
            scorm_frame, blocks = extract_lesson(
                scorm_page=scorm_page,
                scorm_frame=scorm_frame,
                item=lesson_ref,
                total_items=total_lessons,
                sidebar_lesson_links_selector=SIDEBAR_LESSON_LINKS_SELECTOR,
                lesson_content_selector=LESSON_CONTENT_SELECTOR,
                timeout_ms=5000,
            )
            lesson_ref.blocks = blocks

    return CourseScheme(title=course_title, sections=course_scheme)
