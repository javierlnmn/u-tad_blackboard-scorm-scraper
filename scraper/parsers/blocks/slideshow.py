from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scraper.formats.md import Markdown
from scraper.parsers.blocks.base import LessonBlock
from scraper.utils.assets import ensure_asset, safe_basename_from_url, safe_filename


@dataclass
class SlideshowBlock(LessonBlock):
    query_selector = '.block-process'

    intro_title: str = ''
    intro_body_html: str = ''
    intro_body_text: str = ''

    steps: list[tuple[str, str, str, str | None, str]] = field(default_factory=list)
    # (step_num, body_html, body_text, asset_filename, alt)

    image_url_by_filename: dict[str, str] = field(default_factory=dict)  # filename -> url

    def _scrape(self) -> None:
        def _compact(text: str) -> str:
            return (' '.join((text or '').split())).strip()

        def _safe_text_content(el) -> str:
            """Best-effort text extraction without long Playwright auto-waits."""
            try:
                if not el.count():
                    return ''
                return (el.text_content(timeout=1000) or '').strip()
            except Exception:
                return ''

        intro = self.locator.locator('.process-card--intro').first
        if intro.count():
            title_el = intro.locator('.process-card__title .fr-view').first
            self.intro_title = _compact(_safe_text_content(title_el))

            desc_fr = intro.locator('.process-card__description .fr-view').first
            self.intro_body_html = (desc_fr.inner_html() if desc_fr.count() else '') or ''
            self.intro_body_text = _safe_text_content(desc_fr) if desc_fr.count() else ''

        steps: list[tuple[str, str, str, str | None, str]] = []
        image_url_by_filename: dict[str, str] = {}

        cards = self.locator.locator('.process-card[data-slide]')

        for i in range(cards.count()):
            card = cards.nth(i)
            if 'process-card--intro' in (card.get_attribute('class') or ''):
                continue

            num_el = card.locator('.process-card__number p').first
            step_num = _safe_text_content(num_el) if num_el.count() else ''
            step_num = ''.join(ch for ch in step_num if ch.isdigit()) or str(len(steps) + 1)

            # Description
            desc_fr = card.locator('.process-card__description .fr-view').first
            body_html = (desc_fr.inner_html() if desc_fr.count() else '') or ''
            body_text = _safe_text_content(desc_fr) if desc_fr.count() else ''

            # Image (optional)
            img = card.locator('.process-card__media img').first
            asset_filename: str | None = None
            alt = ''
            if img.count():
                alt = (img.get_attribute('alt') or '').strip() or 'image'
                try:
                    url = img.evaluate('el => el.currentSrc || el.src')
                except Exception:
                    url = img.get_attribute('src')

                if url:
                    basename = safe_basename_from_url(url) or 'image'
                    prefix = (self.block_id or 'block').strip()
                    asset_filename = safe_filename(f'{prefix}-step{step_num}-{basename}')
                    image_url_by_filename[asset_filename] = url

            steps.append((step_num, body_html.strip(), body_text.strip(), asset_filename, alt))

        self.steps = steps
        self.image_url_by_filename = image_url_by_filename
        self.intro_body_html = (self.intro_body_html or '').strip()
        self.intro_body_text = (self.intro_body_text or '').strip()

    def _render_md(self, *, assets_dir: Path | None = None) -> str:
        if assets_dir and self.image_url_by_filename:
            for filename, url in self.image_url_by_filename.items():
                ensure_asset(locator=self.locator, url=url, assets_dir=assets_dir, filename=filename)

        intro_md = Markdown.html(self.intro_body_html) or self.intro_body_text or ''

        lines: list[str] = []
        if self.intro_title:
            lines.append(Markdown.heading(4, self.intro_title))
            if intro_md:
                lines.append(intro_md.strip())
            lines.append('')
        elif intro_md:
            lines.append(intro_md.strip())
            lines.append('')

        for step_num, body_html, body_text, asset_filename, alt in self.steps:
            body_md = Markdown.html(body_html) or body_text or ''

            if asset_filename:
                img = Markdown.image(alt or 'image', f'assets/{asset_filename}')
                lines.append(Markdown.numbered_item(step_num, f'{img}\n{body_md}' if body_md else img))
            else:
                lines.append(Markdown.numbered_item(step_num, body_md))

        out = '\n'.join(lines).strip()
        return out if out else (self.locator.text_content() or '').strip()

    def _render_txt(self, *, assets_dir: Path | None = None) -> str:
        parts: list[str] = []
        if self.intro_title:
            parts.append(self.intro_title.strip())
        intro = Markdown.html(self.intro_body_html) or self.intro_body_text
        if intro:
            parts.append(intro.strip())
        for step_num, body_html, body_text, _asset_filename, _alt in self.steps:
            body = Markdown.html(body_html) or body_text
            parts.append(f'{step_num}. {body}'.strip())
        return '\n\n'.join(p for p in parts if p.strip()).strip()
