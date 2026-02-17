from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown
from scraper.parsers.utils.assets import ensure_asset, safe_basename_from_url, safe_filename


@dataclass
class TabsBlock(LessonBlock):
    query_selector = '.blocks-tabs'

    tabs: list[tuple[str, str, str]] = field(default_factory=list)
    # (title, body_html, body_text)

    images: dict[str, str] = field(default_factory=dict)
    # asset_filename -> url

    images_by_tab_index: dict[int, list[tuple[str, str]]] = field(default_factory=dict)
    # tab_index -> [(asset_filename, alt)]

    def _scrape(self) -> None:
        headers = self.locator.locator(f'{self.query_selector} .blocks-tabs__header-item')
        contents = self.locator.locator(f'{self.query_selector} .blocks-tabs__content-item')

        tab_count = min(headers.count(), contents.count())
        tabs: list[tuple[str, str, str]] = []
        images: dict[str, str] = {}
        images_by_tab_index: dict[int, list[tuple[str, str]]] = {}

        prefix = (self.block_id or 'block').strip()

        for i in range(tab_count):
            header = headers.nth(i)
            content = contents.nth(i)

            title_el = header.locator('.fr-view').first
            title = (
                (title_el.text_content() or '').strip()
                if title_el.count()
                else (header.text_content() or '').strip()
            )
            title = ' '.join(title.split())

            desc_fr = content.locator('.blocks-tabs__description .fr-view').first
            body_html = (desc_fr.inner_html() if desc_fr.count() else '') or ''
            body_text = (desc_fr.text_content() or '').strip() if desc_fr.count() else ''

            tabs.append((title, body_html.strip(), body_text.strip()))

            imgs = content.locator('img')
            for j in range(imgs.count()):
                img = imgs.nth(j)
                alt = (img.get_attribute('alt') or '').strip() or 'image'
                try:
                    url = img.evaluate('el => el.currentSrc || el.src')
                except Exception:
                    url = img.get_attribute('src')
                url = (url or '').strip()
                if not url:
                    continue

                basename = safe_basename_from_url(url) or f'image{j + 1}'
                filename = safe_filename(f'{prefix}-tab{i + 1}-img{j + 1}-{basename}')
                images[filename] = url
                images_by_tab_index.setdefault(i, []).append((filename, alt))

        self.tabs = tabs
        self.images = images
        self.images_by_tab_index = images_by_tab_index

    def _render_md(self, *, assets_dir: Path | None = None) -> str:
        if not self.tabs:
            return (self.locator.text_content() or '').strip()

        if assets_dir and self.images:
            for filename, url in self.images.items():
                ensure_asset(locator=self.locator, url=url, assets_dir=assets_dir, filename=filename)

        lines: list[str] = []
        for i, (title, body_html, body_text) in enumerate(self.tabs):
            title = title.strip() or f'Tab {i + 1}'
            body_md = html_fragment_to_markdown(body_html or '').strip()
            if not body_md:
                body_md = body_text or ''

            lines.append(f'- **{title}**  ')

            if body_md:
                for ln in body_md.splitlines():
                    lines.append(('  ' + ln) if ln.strip() else '')

            for filename, alt in self.images_by_tab_index.get(i, []):
                lines.append(f'  ![{alt}](assets/{filename})')

        return '\n'.join(lines).strip()

    def _render_txt(self, *, assets_dir: Path | None = None) -> str:
        if not self.tabs:
            return (self.locator.text_content() or '').strip()

        parts: list[str] = []
        for i, (title, body_html, body_text) in enumerate(self.tabs):
            title = title.strip() or f'Tab {i + 1}'
            body = html_fragment_to_markdown(body_html or '').strip() or body_text
            chunk = title
            if body:
                chunk = f'{chunk}\n{body}'.strip()
            parts.append(chunk)
        return '\n\n'.join(parts).strip()
