from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown
from scraper.parsers.utils.assets import download_via_fetch, safe_basename_from_url, safe_filename


@dataclass()
class LabeledImageBlock(LessonBlock):
    query_selector = '.block-labeled-graphic'

    image_url: str | None = None
    image_alt: str = ''
    asset_filename: str | None = None
    items: list[tuple[str, str]] = field(default_factory=list)  # (title, md_description)

    def _scrape(self) -> None:
        img = self.locator.locator('img.labeled-graphic-canvas__image').first
        if img.count():
            self.image_alt = (img.get_attribute('alt') or '').strip()
            try:
                self.image_url = img.evaluate('el => el.currentSrc || el.src')
            except Exception:
                self.image_url = img.get_attribute('src')

            basename = safe_basename_from_url(self.image_url) or 'image'
            prefix = (self.block_id or 'block').strip()
            self.asset_filename = safe_filename(f'{prefix}-{basename}')

        items: list[tuple[str, str]] = []
        map_items = self.locator.locator('li.map-item')
        for i in range(map_items.count()):
            li = map_items.nth(i)
            title_el = li.locator('h2.bubble__title').first

            title = (title_el.text_content() or '').strip() if title_el.count() else ''
            if not title:
                continue

            desc_fr = li.locator('.bubble__description .fr-view').first
            desc_html = desc_fr.inner_html() if desc_fr.count() else ''
            desc_md = html_fragment_to_markdown(desc_html).strip()
            items.append((title, desc_md))

        self.items = items

        plain_titles = ', '.join(t for t, _ in items)
        self.plain_text = plain_titles if plain_titles else (self.locator.text_content() or '').strip()

        self.markdown = (
            _render_md(
                asset_filename=self.asset_filename,
                image_alt=self.image_alt,
                items=self.items,
            ).strip()
            or self.plain_text
        )

    def render(self, format: str = 'md', *, assets_dir: Path | None = None) -> str:
        if assets_dir and self.image_url and self.asset_filename:
            assets_dir.mkdir(parents=True, exist_ok=True)
            target = assets_dir / self.asset_filename
            if not target.exists():
                data = download_via_fetch(self.locator, self.image_url)
                if data:
                    target.write_bytes(data)

        return super().render(format, assets_dir=assets_dir)


def _render_md(*, asset_filename: str | None, image_alt: str, items: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    if asset_filename:
        alt = image_alt or 'image'
        lines.append(f'![{alt}](assets/{asset_filename})')
        lines.append('')

    for title, desc in items:
        lines.append(f'- **{title}**  ')
        if desc:
            for ln in desc.splitlines():
                lines.append(('  ' + ln) if ln.strip() else '')

    return '\n'.join(lines).strip()
