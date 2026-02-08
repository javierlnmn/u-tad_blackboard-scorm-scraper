"""Write extracted course content to disk."""

import logging
from pathlib import Path

from scraper.models import LessonContent

logger = logging.getLogger(__name__)


def write_course(lessons: list[LessonContent], path: str | Path) -> None:
    """Write lesson texts to a single file, separated by double newlines."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = '\n\n'.join(lesson.text for lesson in lessons)
    path.write_text(content, encoding='utf-8')
    logger.info('Wrote %s lessons to %s', len(lessons), path)
