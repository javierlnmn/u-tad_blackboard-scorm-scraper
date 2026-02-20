from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scraper.parsers.blocks.base import LessonBlock
from scraper.utils.html_to_markdown import html_fragment_to_markdown
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

        intro_md = html_fragment_to_markdown(self.intro_body_html or '').strip()
        if not intro_md:
            intro_md = self.intro_body_text or ''

        lines: list[str] = []
        if self.intro_title:
            lines.append(f'#### {self.intro_title}'.strip())
            if intro_md:
                lines.append(intro_md.strip())
            lines.append('')
        elif intro_md:
            lines.append(intro_md.strip())
            lines.append('')

        for step_num, body_html, body_text, asset_filename, alt in self.steps:
            body_md = html_fragment_to_markdown(body_html or '').strip()
            if not body_md:
                body_md = body_text or ''

            first_line = f'{step_num}.'
            if asset_filename:
                lines.append(f'{first_line} ![{alt or "image"}](assets/{asset_filename})')
                if body_md:
                    for ln in body_md.splitlines():
                        lines.append(('   ' + ln) if ln.strip() else '')
            else:
                body_lines = body_md.splitlines() if body_md else []
                if body_lines:
                    lines.append(f'{first_line} {body_lines[0]}'.rstrip())
                    for ln in body_lines[1:]:
                        lines.append(('   ' + ln) if ln.strip() else '')
                else:
                    lines.append(first_line)

        out = '\n'.join(lines).strip()
        return out if out else (self.locator.text_content() or '').strip()

    def _render_txt(self, *, assets_dir: Path | None = None) -> str:
        parts: list[str] = []
        if self.intro_title:
            parts.append(self.intro_title.strip())
        intro = html_fragment_to_markdown(self.intro_body_html or '').strip() or self.intro_body_text
        if intro:
            parts.append(intro.strip())
        for step_num, body_html, body_text, _asset_filename, _alt in self.steps:
            body = html_fragment_to_markdown(body_html or '').strip() or body_text
            parts.append(f'{step_num}. {body}'.strip())
        return '\n\n'.join(p for p in parts if p.strip()).strip()
