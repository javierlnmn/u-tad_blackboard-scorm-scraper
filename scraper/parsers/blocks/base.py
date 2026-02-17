from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from playwright.sync_api import Locator


@dataclass
class LessonBlock(ABC):
    query_selector: ClassVar[str] = ''

    block_id: str | None
    locator: Locator

    def __post_init__(self) -> None:
        self._scrape()

    @abstractmethod
    def _scrape(self) -> None:
        """Extract and store structured data from the live locator."""
        raise NotImplementedError

    @abstractmethod
    def _render_md(self, *, assets_dir: Path | None = None) -> str:
        """Render this block as Markdown."""
        raise NotImplementedError

    def _render_txt(self, *, assets_dir: Path | None = None) -> str:
        """Render this block as plain text (default: markdown)."""
        return self._render_md(assets_dir=assets_dir)

    def render(self, format: str = 'md', *, assets_dir: Path | None = None) -> str:
        fmt = (format or '').lower().strip()
        fmt = {'markdown': 'md', 'text': 'txt'}.get(fmt, fmt)
        if not fmt:
            fmt = 'md'

        render_fn = getattr(self, f'_render_{fmt}', None)
        if not callable(render_fn):
            render_fn = self._render_md

        out = render_fn(assets_dir=assets_dir)
        return (out or '').rstrip()
