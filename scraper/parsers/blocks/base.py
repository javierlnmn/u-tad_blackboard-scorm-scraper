from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from playwright.sync_api import Locator

from scraper.config import OutputFormat
from scraper.formats.pdf import PDFBuilder


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

    @abstractmethod
    def _render_pdf(self, builder: PDFBuilder, *, assets_dir: Path | None = None) -> list:
        """Return flowables for this block's PDF content."""
        raise NotImplementedError

    def render(self, fmt: OutputFormat = OutputFormat.MD, *, assets_dir: Path | None = None) -> str:
        render_fn = getattr(self, f'_render_{fmt.extension}', None)
        if not callable(render_fn):
            render_fn = self._render_md

        out = render_fn(assets_dir=assets_dir)
        return (out or '').rstrip()
