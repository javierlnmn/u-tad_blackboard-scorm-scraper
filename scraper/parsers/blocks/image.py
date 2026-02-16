from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.utils.assets import download_via_fetch, safe_basename_from_url, safe_filename


@dataclass()
class ImageBlock(LessonBlock):
    query_selector = '.block-image'

    image_url: str | None = None
    image_alt: str = ''
    asset_filename: str | None = None

    def _scrape(self) -> None:
        img = self.locator.locator(f'{self.query_selector} img').first
        if img.count():
            self.image_alt = (img.get_attribute('alt') or '').strip()
            try:
                self.image_url = img.evaluate('el => el.currentSrc || el.src')
            except Exception:
                self.image_url = img.get_attribute('src')

            basename = safe_basename_from_url(self.image_url) or 'image'
            prefix = (self.block_id or 'block').strip()
            self.asset_filename = safe_filename(f'{prefix}-{basename}')

        # Render markdown (download happens in render()).
        if self.asset_filename:
            alt = self.image_alt or 'image'
            self.markdown = f'![{alt}](assets/{self.asset_filename})'
            self.plain_text = alt
        else:
            plain = (self.locator.text_content() or '').strip()
            self.plain_text = plain
            self.markdown = plain

    def render(self, format: str = 'md', *, assets_dir: Path | None = None) -> str:
        if assets_dir and self.image_url and self.asset_filename:
            assets_dir.mkdir(parents=True, exist_ok=True)
            target = assets_dir / self.asset_filename
            if not target.exists():
                data = download_via_fetch(self.locator, self.image_url)
                if data:
                    target.write_bytes(data)

        return super().render(format, assets_dir=assets_dir)
