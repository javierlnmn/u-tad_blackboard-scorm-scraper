from __future__ import annotations

from dataclasses import dataclass

from guesslang import Guess

from scraper.formats.md import Markdown
from scraper.parsers.blocks.base import LessonBlock

_GUESS: Guess | None = None


def _get_guess() -> Guess:
    global _GUESS
    if _GUESS is None:
        _GUESS = Guess()
    return _GUESS


def _md_lang_tag(language_name: str | None) -> str | None:
    if not language_name:
        return None

    raw = language_name.strip()
    if not raw:
        return None

    overrides = {
        'Batchfile': 'bat',
        'C#': 'csharp',
        'C++': 'cpp',
        'CoffeeScript': 'coffeescript',
        'Dockerfile': 'dockerfile',
        'F#': 'fsharp',
        'JavaScript': 'javascript',
        'Objective-C': 'objectivec',
        'PowerShell': 'powershell',
        'Shell': 'bash',
        'TypeScript': 'typescript',
        'Visual Basic': 'vb',
    }
    if raw in overrides:
        return overrides[raw]

    return raw.lower().replace(' ', '')


@dataclass
class CodeBlock(LessonBlock):
    query_selector = 'pre.block-text__code, .block-text--code'

    code: str = ''
    lang: str | None = None

    def _scrape(self) -> None:
        pre = self.locator.locator('pre.block-text__code').first
        code = pre.inner_text() if pre.count() else self.locator.inner_text()
        code = (code or '').rstrip('\n')
        self.code = code

        lang: str | None = None
        if code.strip():
            try:
                lang = _md_lang_tag(_get_guess().language_name(code))
            except Exception:
                lang = None

        self.lang = lang

    def _render_md(self, *, assets_dir=None) -> str:
        return Markdown.code_block(self.code, self.lang)

    def _render_txt(self, *, assets_dir=None) -> str:
        return self.code
