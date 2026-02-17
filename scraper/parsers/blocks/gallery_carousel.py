from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.utils.assets import ensure_asset, safe_basename_from_url, safe_filename


@dataclass
class GalleryCarouselBlock(LessonBlock):
    """Image carousel rendered as a simple vertical image list."""

    query_selector = '.block-gallery-carousel'

    images: list[tuple[str, str, str]] = field(default_factory=list)
    # (asset_filename, alt, url)

    def _scrape(self) -> None:
        imgs = self.locator.locator(f'{self.query_selector} img')

        images: list[tuple[str, str, str]] = []
        prefix = (self.block_id or 'block').strip()

        for i in range(imgs.count()):
            img = imgs.nth(i)
            alt = (img.get_attribute('alt') or '').strip()

            try:
                url = img.evaluate('el => el.currentSrc || el.src')
            except Exception:
                url = img.get_attribute('src')
            url = (url or '').strip()

            if not url:
                continue

            basename = safe_basename_from_url(url) or f'image{i + 1}'
            filename = safe_filename(f'{prefix}-carousel{i + 1}-{basename}')
            images.append((filename, alt or 'image', url))

        self.images = images

    def _render_md(self, *, assets_dir: Path | None = None) -> str:
        if not self.images:
            return (self.locator.text_content() or '').strip()

        if assets_dir:
            for filename, _alt, url in self.images:
                ensure_asset(locator=self.locator, url=url, assets_dir=assets_dir, filename=filename)

        return '\n\n'.join(f'![{alt}](assets/{filename})' for filename, alt, _ in self.images).strip()

    def _render_txt(self, *, assets_dir: Path | None = None) -> str:
        if not self.images:
            return (self.locator.text_content() or '').strip()

        return '\n'.join(url for _filename, _alt, url in self.images if url).strip()
