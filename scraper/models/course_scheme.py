from dataclasses import dataclass


@dataclass
class CourseSchemeLesson:
    """
    A reference to a lesson entry in the course scheme.
    """

    index: int  # Global index
    title: str
    href: str | None = None
    lesson_id: str | None = None


@dataclass
class CourseSchemeSection:
    """
    A section/module in the course scheme that contains lessons.
    """

    title: str
    lessons: list[CourseSchemeLesson]
