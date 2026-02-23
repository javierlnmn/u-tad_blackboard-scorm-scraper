from dataclasses import dataclass

from scraper.parsers.blocks import LessonBlock


@dataclass
class LessonContent:
    label: str
    blocks: list[LessonBlock]
