from __future__ import annotations

from dataclasses import dataclass

from scraper.config import get_config
from scraper.parsers.blocks.base import LessonBlock
from scraper.utils.assets import ensure_asset, safe_basename_from_url, safe_filename


@dataclass
class VideoBlock(LessonBlock):
    query_selector = '.block-video'

    video_url: str | None = None
    video_asset_filename: str | None = None

    poster_url: str | None = None
    poster_asset_filename: str | None = None

    def _scrape(self) -> None:
        # Try <video src>, then <source src>.
        video = self.locator.locator(f'{self.query_selector} video').first
        source = self.locator.locator(f'{self.query_selector} video source').first

        url: str | None = None
        if video.count():
            try:
                url = video.evaluate('el => el.currentSrc || el.src')
            except Exception:
                url = video.get_attribute('src')

        if (not url) and source.count():
            url = source.get_attribute('src')

        url = (url or '').strip() or None
        self.video_url = url

        poster: str | None = None
        if video.count():
            poster = (video.get_attribute('poster') or '').strip() or None
        if not poster:
            # Some variants include <img> inside poster container.
            img = self.locator.locator(f'{self.query_selector} img').first
            if img.count():
                poster = (img.get_attribute('src') or '').strip() or None
        self.poster_url = poster

        prefix = (self.block_id or 'block').strip()
        if self.video_url:
            base = safe_basename_from_url(self.video_url) or 'video.mp4'
            self.video_asset_filename = safe_filename(f'{prefix}-{base}')
        if self.poster_url:
            base = safe_basename_from_url(self.poster_url) or 'poster.jpg'
            self.poster_asset_filename = safe_filename(f'{prefix}-{base}')

    def _render_video_unavailable(self) -> str:
        msg = 'Video is not available in this output.'
        if self.video_url:
            msg = f'{msg} Source: {self.video_url}'
        return '\n'.join([f'> {line}'.rstrip() for line in msg.splitlines()]).strip()

    def _render_md(self, builder, assets_dir=None) -> str:
        if not self.video_url:
            return self._render_video_unavailable()

        if not get_config().download_videos:
            return f'> [Link al vídeo]({self.video_url})'

        if not self.video_asset_filename or not assets_dir:
            return self._render_video_unavailable()

        ok = ensure_asset(
            locator=self.locator,
            url=self.video_url,
            assets_dir=assets_dir,
            filename=self.video_asset_filename,
        )
        if not ok:
            return self._render_video_unavailable()
        poster_attr = ''
        if self.poster_url and self.poster_asset_filename and assets_dir:
            if ensure_asset(
                locator=self.locator,
                url=self.poster_url,
                assets_dir=assets_dir,
                filename=self.poster_asset_filename,
            ):
                poster_attr = f' poster="assets/{self.poster_asset_filename}"'
        return (
            f'<video controls preload="metadata" src="assets/{self.video_asset_filename}"{poster_attr}>'
            f'</video>'
        ).strip()

    def _render_pdf(self, builder, assets_dir=None) -> list:
        if not self.video_url:
            return builder.build_callout('Video is not available in this output.')
        return builder.build_callout(href=self.video_url, link_text='Link al vídeo')
