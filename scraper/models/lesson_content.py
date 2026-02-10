from dataclasses import dataclass


@dataclass
class LessonContentPart:
    # TODO: Implement different lesson contents
    text: str


@dataclass
class LessonContent:
    """Text content extracted for one lesson."""

    label: str
    contents: list[LessonContentPart]
