from __future__ import annotations

import base64
from dataclasses import dataclass, field
from pathlib import Path

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown


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

            basename = _safe_basename_from_url(self.image_url) or 'image'
            prefix = (self.block_id or 'block').strip()
            self.asset_filename = _safe_filename(f'{prefix}-{basename}')

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
                data = _download_via_fetch(self.locator, self.image_url)
                if data:
                    target.write_bytes(data)

        return super().render(format, assets_dir=assets_dir)


def _safe_basename_from_url(url: str | None) -> str | None:
    if not url:
        return None
    base = url.split('?', 1)[0].split('#', 1)[0].rstrip('/').split('/')[-1]
    return base or None


def _safe_filename(name: str) -> str:
    name = name.strip()
    name = ''.join(ch if ch.isalnum() or ch in {'.', '-', '_'} else '_' for ch in name)
    name = name.strip('._-') or 'asset'
    return name


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


def _download_via_fetch(locator, url: str) -> bytes | None:
    js = r"""
async (el, url) => {
  const res = await fetch(url);
  if (!res.ok) return null;
  const buf = await res.arrayBuffer();
  const bytes = new Uint8Array(buf);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}
"""
    try:
        b64 = locator.evaluate(js, url)
    except Exception:
        return None
    if not b64:
        return None
    try:
        return base64.b64decode(b64)
    except Exception:
        return None
