from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock
from scraper.utils.html_to_markdown import html_fragment_to_markdown


@dataclass
class NumberedListBlock(LessonBlock):
    query_selector = '.block-list.block-list--numbered'

    items: list[tuple[str, str]] = field(default_factory=list)  # (num, item_html)

    def _scrape(self) -> None:
        items: list[tuple[str, str]] = []

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
            items.append((num, (html or '').strip()))

        self.items = items

    def _render_md(self, *, assets_dir=None) -> str:
        if not self.items:
            return (self.locator.text_content() or '').strip()

        rendered: list[str] = []
        for num, item_html in self.items:
            md = html_fragment_to_markdown(item_html or '').strip()
            if not md:
                md = ''
            rendered.append(_render_numbered_item(num, md))
        return '\n'.join(r for r in rendered if r.strip()).strip()

    def _render_txt(self, *, assets_dir=None) -> str:
        if not self.items:
            return (self.locator.text_content() or '').strip()

        rendered: list[str] = []
        for num, item_html in self.items:
            md = html_fragment_to_markdown(item_html or '').strip()
            rendered.append(f'{num}. {md}'.strip())
        return '\n'.join(r for r in rendered if r.strip()).strip()


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
