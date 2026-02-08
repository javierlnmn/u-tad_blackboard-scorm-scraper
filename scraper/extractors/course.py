"""Extract lesson content from a SCORM (Rise) page."""

import logging
import time

from playwright.sync_api import Page

from scraper.extractors.sidebar import SIDEBAR_LESSON_LINKS_SELECTOR, parse_sidebar
from scraper.models import LessonContent

logger = logging.getLogger(__name__)

CONTENT_FRAME = '#content-frame'
LESSON_CONTENT_SELECTOR = '[data-lesson-id]'
SIDEBAR_SELECTOR = '#nav-content-sidebar'


def extract_course(scorm_page: Page) -> list[LessonContent]:
    """
    From an open SCORM popup page, click each sidebar lesson and collect content.

    Returns a list of LessonContent in sidebar order.
    """
    sidebar = scorm_page.locator(SIDEBAR_SELECTOR)
    sidebar.wait_for(state='visible')
    sidebar_html = sidebar.inner_html()
    wrapped = f'<div id="nav-content-sidebar">{sidebar_html}</div>'
    items = parse_sidebar(wrapped)

    if not items:
        logger.warning('No sidebar items found.')
        return []

    content_frame = scorm_page.frame_locator(CONTENT_FRAME)
    lessons: list[LessonContent] = []

    for item in items:
        link = scorm_page.locator(SIDEBAR_LESSON_LINKS_SELECTOR).nth(item.index)
        link.click()
        time.sleep(0.5)
        content_frame.locator(LESSON_CONTENT_SELECTOR).wait_for(state='visible', timeout=5000)
        lesson_el = content_frame.locator(LESSON_CONTENT_SELECTOR).first
        text = lesson_el.inner_text()
        lessons.append(LessonContent(label=item.label, text=text))
        logger.info('Scraped %s/%s: %s', item.index + 1, len(items), item.label)

    return lessons
