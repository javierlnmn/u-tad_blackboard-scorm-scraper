from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock
from scraper.parsers.html_to_markdown import html_fragment_to_markdown


@dataclass
class FlashcardsBlock(LessonBlock):
    query_selector = '.block-flashcards'

    cards: list[tuple[str, str]] = field(default_factory=list)  # (front_title, back_md)

    def _scrape(self) -> None:
        cards: list[tuple[str, str]] = []

        flashcards = self.locator.locator('li.flashcard')
        for i in range(flashcards.count()):
            li = flashcards.nth(i)

            front_fr = li.locator('.flashcard-side--front .fr-view').first
            front_text = (front_fr.text_content() or '').strip() if front_fr.count() else ''
            front_text = ' '.join(front_text.split())
            if not front_text:
                continue

            back_fr = li.locator('.flashcard-side--back .fr-view').first
            back_html = back_fr.inner_html() if back_fr.count() else ''
            back_md = html_fragment_to_markdown(back_html).strip()
            if not back_md and back_fr.count():
                back_md = (back_fr.text_content() or '').strip()

            cards.append((front_text, back_md))

        self.cards = cards
        self.plain_text = (
            ', '.join(title for title, _ in cards) if cards else (self.locator.text_content() or '').strip()
        )
        self.markdown = _render_flashcards_md(cards)

    def render(self, format: str = 'md', *, assets_dir=None) -> str:
        return super().render(format, assets_dir=assets_dir)


def _render_flashcards_md(cards: list[tuple[str, str]]) -> str:
    lines: list[str] = []
    for title, desc in cards:
        # Hard break after title so it renders on next line inside list items
        lines.append(f'- **{title}**  ')
        if desc:
            for ln in desc.splitlines():
                lines.append(('  ' + ln) if ln.strip() else '')
    return '\n'.join(lines).strip()
