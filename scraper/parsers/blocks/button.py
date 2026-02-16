from __future__ import annotations

from dataclasses import dataclass

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown


@dataclass
class ButtonBlock(LessonBlock):
    query_selector = '.blocks-button'

    href: str | None = None

    def _scrape(self) -> None:
        desc_fr = self.locator.locator('.blocks-button__description .fr-view').first
        desc_html = desc_fr.inner_html() if desc_fr.count() else ''
        desc_md = html_fragment_to_markdown(desc_html).strip()

        button = self.locator.locator('a.blocks-button__button[href]').first
        self.href = (button.get_attribute('href') or '').strip() if button.count() else None
        if not self.href:
            self.href = None

        self.plain_text = desc_md or (self.locator.text_content() or '').strip()
        self.markdown = _render_callout(desc_md or self.plain_text, self.href)

    def render(self, format: str = 'md', *, assets_dir=None) -> str:
        return super().render(format, assets_dir=assets_dir)


def _render_callout(text: str, href: str | None) -> str:
    lines: list[str] = []
    body = (text or '').strip()
    if body:
        for ln in body.splitlines():
            lines.append(f'> {ln}'.rstrip())

    # Add a blank line within the callout only if needed.
    if href:
        if lines:
            lines.append('>')
        lines.append(f'> [Link]({href})')

    return '\n'.join(lines).strip()
