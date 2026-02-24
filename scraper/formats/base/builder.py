from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CourseBuilder(ABC):
    @abstractmethod
    def add_elements(self, elements: Any) -> None: ...

    @abstractmethod
    def build(self) -> None: ...
