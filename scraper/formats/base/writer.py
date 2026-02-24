from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class CourseWriter(ABC):
    @abstractmethod
    def write(
        self,
        course,
        output_path: Path,
        assets_dir: Path,
    ) -> None: ...
