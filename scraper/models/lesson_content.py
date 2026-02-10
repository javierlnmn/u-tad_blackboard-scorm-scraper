from dataclasses import dataclass

from scraper.parsers.blocks import LessonBlock


@dataclass
class LessonContent:
    """Text content extracted for one lesson."""

    label: str
    blocks: list[LessonBlock]
