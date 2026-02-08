from dataclasses import dataclass


@dataclass
class SidebarItem:
    """A single clickable item in the SCORM nav sidebar."""

    index: int
    label: str
    href: str | None = None


@dataclass
class LessonContent:
    """Text content extracted for one lesson."""

    label: str
    text: str
