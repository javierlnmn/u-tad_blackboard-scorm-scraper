from __future__ import annotations

import logging
from pathlib import Path

from scraper.models.lesson_content import LessonContent

logger = logging.getLogger(__name__)


def _render_plain_text(lessons: list[LessonContent]) -> str:
    chunks: list[str] = []

    for lesson in lessons:
        chunks.append(lesson.label.strip())
        for block in lesson.blocks:
            rendered = block.render('md').strip()
            if rendered:
                chunks.append(rendered)

        chunks.append('')

    return '\n\n'.join(c for c in chunks if c is not None).rstrip() + '\n'


def write_course(lessons: list[LessonContent], path: str | Path, *, output_format: str = 'md') -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fmt = (output_format or '').lower().strip()

    if fmt not in {'md', 'markdown', 'pdf', 'txt', 'text', 'plain', ''}:
        raise ValueError(f'Unknown output_format: {output_format!r}')

    content = _render_plain_text(lessons)
    path.write_text(content, encoding='utf-8')

    logger.info('Wrote %s lessons to %s', len(lessons), path)
