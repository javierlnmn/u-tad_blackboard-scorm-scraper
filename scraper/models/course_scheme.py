from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock


@dataclass
class CourseSchemeLesson:
    index: int  # Global index
    title: str
    href: str | None = None
    lesson_id: str | None = None
    blocks: list[LessonBlock] = field(default_factory=list)


@dataclass
class CourseSchemeSection:
    title: str
    lessons: list[CourseSchemeLesson]


@dataclass
class CourseScheme:
    title: str
    sections: list[CourseSchemeSection]
