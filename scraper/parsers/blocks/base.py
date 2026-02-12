from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from playwright.sync_api import Locator


@dataclass(slots=True)
class LessonBlock(ABC):
    query_selector: ClassVar[str] = ''

    block_id: str | None
    locator: Locator
    plain_text: str = ''
    markdown: str = ''

    def __post_init__(self) -> None:
        self._scrape()

    @abstractmethod
    def _scrape(self) -> None:
        """Populate plain_text/markdown from the live locator."""
        raise NotImplementedError

    @abstractmethod
    def render(self, format: str = 'md') -> str:
        fmt = (format or '').lower().strip()
        if fmt in {'md', 'markdown', ''}:
            return self.markdown
        return self.plain_text
