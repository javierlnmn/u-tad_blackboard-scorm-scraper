from __future__ import annotations

from dataclasses import dataclass

from scraper.formats.md import Markdown
from scraper.formats.pdf import html_to_flowables
from scraper.parsers.blocks.base import LessonBlock


@dataclass
class ButtonBlock(LessonBlock):
    query_selector = '.blocks-button'

    href: str | None = None
    description_html: str = ''
    description_text: str = ''

    def _scrape(self) -> None:
        desc_fr = self.locator.locator('.blocks-button__description .fr-view').first
        self.description_html = desc_fr.inner_html() if desc_fr.count() else ''
        self.description_text = (desc_fr.text_content() or '').strip() if desc_fr.count() else ''

        button = self.locator.locator('a.blocks-button__button[href]').first
        self.href = (button.get_attribute('href') or '').strip() if button.count() else None
        if not self.href:
            self.href = None

        self.description_html = (self.description_html or '').strip()
        self.description_text = (self.description_text or '').strip() or (
            self.locator.text_content() or ''
        ).strip()

    def _render_md(self, *, assets_dir=None) -> str:
        desc_md = Markdown.html(self.description_html)
        body = desc_md or (self.description_text or '')
        return Markdown.link_callout(body, self.href)

    def _render_pdf(self, builder, *, assets_dir=None) -> list:
        if not (self.description_html or self.description_text or self.href):
            return []
        body_flows = html_to_flowables(
            self.description_html or self.description_text or '',
            builder,
            assets_dir=assets_dir,
        )
        return builder.build_callout(
            body=(self.description_text or '') if not body_flows else None,
            href=self.href,
            body_flowables=body_flows if body_flows else None,
            link_text='View link',
        )
