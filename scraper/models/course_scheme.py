from __future__ import annotations

from dataclasses import dataclass, field

from scraper.parsers.blocks.base import LessonBlock


@dataclass
class CourseSchemeLesson:
    """
    A reference to a lesson entry in the course scheme.
    """

    index: int  # Global index
    title: str
    href: str | None = None
    lesson_id: str | None = None
    blocks: list[LessonBlock] = field(default_factory=list)


@dataclass
class CourseSchemeSection:
    """
    A section/module in the course scheme that contains lessons.
    """

    title: str
    lessons: list[CourseSchemeLesson]


@dataclass
class CourseScheme:
    """
    A course scheme that contains sections
    """

    title: str
    sections: list[CourseSchemeSection]
