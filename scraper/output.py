from __future__ import annotations

import logging
from pathlib import Path

from scraper.models.course_scheme import CourseScheme

logger = logging.getLogger(__name__)


def _slugify_md_heading(text: str) -> str:
    s = (text or '').strip().lower()
    out: list[str] = []
    prev_dash = False
    for ch in s:
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
            continue
        if ch in {' ', '-'}:
            if not prev_dash:
                out.append('-')
                prev_dash = True
            continue
        # drop punctuation (.,:() etc.)
    slug = ''.join(out).strip('-')
    return slug or 'section'


def _render_index(entries: list[tuple[int, str]]) -> str:
    used: dict[str, int] = {}
    lines: list[str] = ['## Index', '']

    for level, heading in entries:
        base = _slugify_md_heading(heading)
        n = used.get(base, 0)
        used[base] = n + 1
        anchor = base if n == 0 else f'{base}-{n + 1}'

        indent = '  ' * max(0, level - 2)
        lines.append(f'{indent}- [{heading}](#{anchor})')

    lines.append('')
    return '\n'.join(lines)


def _render_plain_text(course: CourseScheme, *, assets_dir: Path | None = None) -> str:
    chunks: list[str] = []

    chunks.append(f'# {course.title}'.strip())
    chunks.append('')

    index_entries: list[tuple[int, str]] = []
    for section_idx, section in enumerate(course.sections, start=1):
        index_entries.append((2, f'{section_idx}. {section.title}'.strip()))
        for lesson_idx, lesson in enumerate(section.lessons, start=1):
            index_entries.append((3, f'{section_idx}.{lesson_idx} {lesson.title}'.strip()))

    if index_entries:
        chunks.append(_render_index(index_entries).strip())
        chunks.append('')

    for section_idx, section in enumerate(course.sections, start=1):
        chunks.append(f'## {section_idx}. {section.title}'.strip())
        chunks.append('')

        for lesson_idx, lesson in enumerate(section.lessons, start=1):
            chunks.append(f'### {section_idx}.{lesson_idx} {lesson.title}'.strip())
            chunks.append('')

            for block in lesson.blocks:
                rendered = block.render('md', assets_dir=assets_dir).strip()
                if rendered:
                    chunks.append(rendered)
                    chunks.append('')

    return '\n\n'.join(c for c in chunks if c is not None).rstrip() + '\n'


def write_course(course: CourseScheme, path: str | Path, *, output_format: str = 'md') -> None:
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / 'assets'

    fmt = (output_format or '').lower().strip()

    if fmt not in {'md', 'markdown', 'pdf', 'txt', 'text', 'plain', ''}:
        raise ValueError(f'Unknown output_format: {output_format!r}')

    filename = f'{course.title}.{fmt or "md"}'
    safe_filename = ''.join(
        ch if ch.isalnum() or ch in {'.', '-', '_', ' '} else '_' for ch in filename
    ).strip()
    safe_filename = safe_filename.replace('  ', ' ').strip() or f'course.{fmt or "md"}'
    output_file = output_dir / safe_filename

    content = _render_plain_text(course, assets_dir=assets_dir)
    output_file.write_text(content, encoding='utf-8')

    lessons_count = sum(len(s.lessons) for s in course.sections)
    logger.info('Wrote %s lessons to %s', lessons_count, output_file)
