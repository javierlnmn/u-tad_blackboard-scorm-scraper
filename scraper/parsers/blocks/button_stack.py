from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.blocks.button import _render_callout
from scraper.parsers.html_to_markdown import html_fragment_to_markdown


@dataclass
class ButtonStackBlock(LessonBlock):
    query_selector = '.blocks-buttonstack'

    entries: list[tuple[str, str | None]] = field(default_factory=list)  # (desc_md, href)

    def _scrape(self) -> None:
        containers = self.locator.locator(f'{self.query_selector} .blocks-button__container')

        entries: list[tuple[str, str | None]] = []
        for i in range(containers.count()):
            container = containers.nth(i)

            desc_fr = container.locator('.blocks-button__description .fr-view').first
            desc_html = desc_fr.inner_html() if desc_fr.count() else ''
            desc_md = html_fragment_to_markdown(desc_html).strip()

            button = container.locator('a.blocks-button__button[href]').first
            href = (button.get_attribute('href') or '').strip() if button.count() else None
            if not href:
                href = None

            if not desc_md and not href:
                continue

            entries.append((desc_md, href))

        self.entries = entries

        if not entries:
            plain = (self.locator.text_content() or '').strip()
            self.plain_text = plain
            self.markdown = plain
            return

        self.plain_text = '\n'.join((d or '').strip() for d, _ in entries if (d or '').strip()).strip()
        self.markdown = '\n\n'.join(_render_callout(desc or '', href) for desc, href in entries).strip()
