from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown
from scraper.parsers.utils.assets import download_via_fetch, safe_basename_from_url, safe_filename


@dataclass
class SlideshowBlock(LessonBlock):
    # Rendered in the UI as a step/slide process.
    query_selector = '.block-process'

    intro_title: str = ''
    intro_body_md: str = ''
    steps: list[tuple[str, str, str | None, str]] = field(default_factory=list)
    # (step_num, body_md, asset_filename, alt)

    image_url_by_filename: dict[str, str] = field(default_factory=dict)

    def _scrape(self) -> None:
        # Intro slide
        intro = self.locator.locator('.process-card--intro').first
        if intro.count():
            title_el = intro.locator('.process-card__title .fr-view').first
            self.intro_title = (' '.join((title_el.text_content() or '').split())).strip()

            desc_fr = intro.locator('.process-card__description .fr-view').first
            desc_html = desc_fr.inner_html() if desc_fr.count() else ''
            self.intro_body_md = html_fragment_to_markdown(desc_html).strip()

        # Step slides
        steps: list[tuple[str, str, str | None, str]] = []
        image_url_by_filename: dict[str, str] = {}

        cards = self.locator.locator('.process-card[data-slide]')

        for i in range(cards.count()):
            card = cards.nth(i)
            if 'process-card--intro' in (card.get_attribute('class') or ''):
                continue

            num_el = card.locator('.process-card__number p').first
            step_num = (num_el.text_content() or '').strip() if num_el.count() else ''
            step_num = ''.join(ch for ch in step_num if ch.isdigit()) or str(len(steps) + 1)

            # Description
            desc_fr = card.locator('.process-card__description .fr-view').first
            desc_html = desc_fr.inner_html() if desc_fr.count() else ''
            body_md = html_fragment_to_markdown(desc_html).strip()
            if not body_md and desc_fr.count():
                body_md = (desc_fr.text_content() or '').strip()

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

            steps.append((step_num, body_md, asset_filename, alt))

        self.steps = steps
        self.image_url_by_filename = image_url_by_filename

        # Markdown render
        self.markdown = _render_md(self.intro_title, self.intro_body_md, self.steps)
        self.plain_text = self.markdown

    def render(self, format: str = 'md', *, assets_dir: Path | None = None) -> str:
        if assets_dir and self.image_url_by_filename:
            assets_dir.mkdir(parents=True, exist_ok=True)
            for filename, url in self.image_url_by_filename.items():
                target = assets_dir / filename
                if target.exists():
                    continue
                data = download_via_fetch(self.locator, url)
                if data:
                    target.write_bytes(data)

        return super().render(format, assets_dir=assets_dir)


def _render_md(intro_title: str, intro_body: str, steps: list[tuple[str, str, str | None, str]]) -> str:
    lines: list[str] = []

    if intro_title:
        lines.append(f'#### {intro_title}'.strip())
        if intro_body:
            lines.append(intro_body.strip())
        lines.append('')

    # Numbered list for steps
    for step_num, body_md, asset_filename, alt in steps:
        first_line = f'{step_num}.'
        if asset_filename:
            # Put image right after the marker to keep the structure compact.
            lines.append(f'{first_line} ![{alt}](assets/{asset_filename})')
            if body_md:
                for ln in body_md.splitlines():
                    lines.append(('   ' + ln) if ln.strip() else '')
        else:
            # No image: render body on same line if possible.
            body_lines = body_md.splitlines() if body_md else []
            if body_lines:
                lines.append(f'{first_line} {body_lines[0]}'.rstrip())
                for ln in body_lines[1:]:
                    lines.append(('   ' + ln) if ln.strip() else '')
            else:
                lines.append(first_line)

    return '\n'.join(lines).strip()

