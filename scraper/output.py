import logging
from pathlib import Path

from scraper.models.lesson_content import LessonContent

logger = logging.getLogger(__name__)


def _render_plain_text(lessons: list[LessonContent]) -> str:
    return '\n\n'.join(lesson.text for lesson in lessons).strip() + '\n'


def write_course(lessons: list[LessonContent], path: str | Path, *, output_format: str = 'md') -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fmt = (output_format or '').lower().strip()

    if fmt not in {'md', 'markdown', 'pdf', 'txt', 'text', 'plain', ''}:
        raise ValueError(f'Unknown output_format: {output_format!r}')

    content = _render_plain_text(lessons)
    path.write_text(content, encoding='utf-8')

    logger.info('Wrote %s lessons to %s', len(lessons), path)
