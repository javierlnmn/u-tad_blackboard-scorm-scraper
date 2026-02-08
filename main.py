import logging
import sys

from playwright.sync_api import sync_playwright

from scraper.config import load_settings
from scraper.extractors.course import extract_course
from scraper.output import write_course

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main() -> None:
    settings = load_settings()

    if not settings.base_url:
        logger.error('BLACKBOARD_URL is not set. Set it in .env or as environment variable.')
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': settings.viewport_width, 'height': settings.viewport_height}
        )
        page = context.new_page()
        page.goto(settings.base_url)

        print('Log in to Blackboard and open the SCORM in pop-up mode.')
        with page.expect_popup() as popup_info:
            input('Press ENTER after the SCORM popup is open.')

        scorm_page = popup_info.value
        scorm_page.wait_for_load_state()

        lessons = extract_course(scorm_page)
        write_course(lessons, settings.output_path)


if __name__ == '__main__':
    main()
