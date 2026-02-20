from __future__ import annotations

from dataclasses import dataclass, field

from scraper.formats.md import Markdown
from scraper.parsers.blocks.base import LessonBlock


@dataclass
class FlashcardsBlock(LessonBlock):
    query_selector = '.block-flashcards'

    cards: list[tuple[str, str]] = field(default_factory=list)  # (front_title, back_html)

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
            cards.append((front_text, (back_html or '').strip()))

        self.cards = cards

    def _render_md(self, *, assets_dir=None) -> str:
        if not self.cards:
            return (self.locator.text_content() or '').strip()

        lines: list[str] = []
        for title, back_html in self.cards:
            back_md = Markdown.html(back_html)
            lines.append(Markdown.bullet_item(title, back_md))
        return '\n'.join(lines).strip()

    def _render_txt(self, *, assets_dir=None) -> str:
        if not self.cards:
            return (self.locator.text_content() or '').strip()

        parts: list[str] = []
        for title, back_html in self.cards:
            back = Markdown.html(back_html)
            chunk = title
            if back:
                chunk = f'{chunk}\n{back}'.strip()
            parts.append(chunk)
        return '\n\n'.join(parts).strip()
