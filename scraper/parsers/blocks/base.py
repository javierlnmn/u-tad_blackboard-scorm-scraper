from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from playwright.sync_api import Locator


@dataclass(slots=True)
class LessonBlock(ABC):
    block_id: str | None
    locator: Locator
    plain_text: str = ''
    markdown: str = ''

    def __post_init__(self) -> None:
        self._parse()

    @abstractmethod
    def _parse(self) -> None:
        """Populate plain_text/markdown from the live locator."""
        raise NotImplementedError

    @abstractmethod
    def render(self, format: str = 'md') -> str:
        fmt = (format or '').lower().strip()
        if fmt in {'md', 'markdown', ''}:
            return self.markdown
        return self.plain_text
