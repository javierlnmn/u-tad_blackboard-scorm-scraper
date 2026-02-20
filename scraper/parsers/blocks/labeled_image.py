from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scraper.formats.md import Markdown
from scraper.parsers.blocks.base import LessonBlock
from scraper.utils.assets import ensure_asset, safe_basename_from_url, safe_filename


@dataclass()
class LabeledImageBlock(LessonBlock):
    query_selector = '.block-labeled-graphic'

    image_url: str | None = None
    image_alt: str = ''
    asset_filename: str | None = None
    items: list[tuple[str, str]] = field(default_factory=list)  # (title, desc_html)

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
            items.append((title, (desc_html or '').strip()))

        self.items = items

        self.image_url = (self.image_url or '').strip() or None
        self.asset_filename = (self.asset_filename or '').strip() or None
        self.image_alt = (self.image_alt or '').strip()

    def _render_md(self, *, assets_dir: Path | None = None) -> str:
        if assets_dir and self.image_url and self.asset_filename:
            ensure_asset(
                locator=self.locator,
                url=self.image_url,
                assets_dir=assets_dir,
                filename=self.asset_filename,
            )

        lines: list[str] = []
        if self.asset_filename:
            alt = self.image_alt or 'image'
            lines.append(Markdown.image(alt, f'assets/{self.asset_filename}'))
            lines.append('')

        for title, desc_html in self.items:
            desc_md = Markdown.html(desc_html)
            lines.append(Markdown.bullet_item(title, desc_md))

        out = '\n'.join(lines).strip()
        return out if out else (self.locator.text_content() or '').strip()

    def _render_txt(self, *, assets_dir: Path | None = None) -> str:
        parts: list[str] = []
        if self.image_alt:
            parts.append(self.image_alt.strip())
        if self.image_url:
            parts.append(self.image_url)
        for title, desc_html in self.items:
            desc_txt = Markdown.html(desc_html)
            chunk = title
            if desc_txt:
                chunk = f'{chunk}\n{desc_txt}'.strip()
            parts.append(chunk)
        return '\n\n'.join(p for p in parts if p.strip()).strip()
