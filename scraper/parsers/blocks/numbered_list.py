from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown


@dataclass
class NumberedListBlock(LessonBlock):
    query_selector = '.block-list.block-list--numbered'

    items: list[str] = field(default_factory=list)

    def _scrape(self) -> None:
        items: list[str] = []

        lis = self.locator.locator('ol.block-list__list > li.block-list__item--numbered')
        if not lis.count():
            lis = self.locator.locator('.block-list--numbered li.block-list__item--numbered')

        for i in range(lis.count()):
            li = lis.nth(i)

            num_el = li.locator('.block-list__number').first
            num = (num_el.text_content() or '').strip() if num_el.count() else ''
            if not num.isdigit():
                num = str(i + 1)

            fr = li.locator('.block-list__content .fr-view').first
            html = fr.inner_html() if fr.count() else ''
            md = html_fragment_to_markdown(html).strip()
            if not md:
                md = (li.text_content() or '').strip()

            items.append(_render_numbered_item(num, md))

        self.items = items
        self.markdown = '\n'.join(items).strip()
        self.plain_text = '\n'.join(i for i in items if i.strip()).strip()

    def render(self, format: str = 'md', *, assets_dir=None) -> str:
        return super().render(format, assets_dir=assets_dir)


def _render_numbered_item(num: str, md: str) -> str:
    prefix = f'{num}. '
    lines = md.splitlines() if md else ['']
    if not lines:
        return prefix.rstrip()

    out = [prefix + lines[0].strip()]
    indent = ' ' * len(prefix)
    for ln in lines[1:]:
        out.append((indent + ln) if ln.strip() else '')
    return '\n'.join(out).rstrip()

