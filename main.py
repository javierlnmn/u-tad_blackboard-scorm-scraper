import logging
import sys

from playwright.sync_api import sync_playwright

from scraper.config import get_config
from scraper.extractors.course import extract_course
from scraper.output import write_course
from scraper.setup import run_setup_wizard

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main() -> None:
    run_setup_wizard()
    settings = get_config()

    if not settings.base_url:
        logger.error('Base URL is not set.')
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': settings.viewport_width, 'height': settings.viewport_height},
            screen={'width': settings.viewport_width, 'height': settings.viewport_height},
        )
        page = context.new_page()
        page.goto(settings.base_url)

        logger.info('Log in to Blackboard and open the SCORM in pop-up mode.')
        with page.expect_popup() as popup_info:
            input('Press ENTER after the SCORM popup is open.')

        scorm_page = popup_info.value
        scorm_page.set_viewport_size({'width': settings.viewport_width, 'height': settings.viewport_height})
        scorm_page.wait_for_load_state()

        lessons = extract_course(scorm_page)
        write_course(lessons, settings.output_path, output_format=settings.output_format)


if __name__ == '__main__':
    main()
