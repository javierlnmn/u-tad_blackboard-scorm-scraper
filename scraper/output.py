from __future__ import annotations

import logging
from pathlib import Path

from scraper.config import OutputFormat
from scraper.models.course_scheme import CourseScheme

logger = logging.getLogger(__name__)


def write_course(
    course: CourseScheme,
    path: str | Path,
    *,
    output_format: OutputFormat | str = OutputFormat.MD,
    pdf_theme: str | None = None,
) -> None:
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / 'assets'

    fmt = (
        output_format
        if isinstance(output_format, OutputFormat)
        else OutputFormat.from_extension(output_format)
    )

    filename = f'{course.title}.{fmt.extension}'
    safe_filename = ''.join(
        ch if ch.isalnum() or ch in {'.', '-', '_', ' '} else '_' for ch in filename
    ).strip()
    safe_filename = safe_filename.replace('  ', ' ').strip() or f'course.{fmt.extension}'
    output_file = output_dir / safe_filename

    write_file(course, output_file, fmt, assets_dir=assets_dir, pdf_theme=pdf_theme)

    lessons_count = sum(len(s.lessons) for s in course.sections)
    logger.info('Wrote %s lessons to %s', lessons_count, output_file)


def write_file(
    course: CourseScheme,
    output_path: Path,
    fmt: OutputFormat,
    *,
    assets_dir: Path,
    pdf_theme: str | None = None,
) -> None:
    """Write course to file in the given format."""
    if fmt == OutputFormat.MD:
        from scraper.formats.md import write_course as write_md

        write_md(course, output_path, assets_dir=assets_dir)
    elif fmt == OutputFormat.PDF:
        from scraper.formats.pdf import write_course as write_pdf

        write_pdf(course, output_path, assets_dir=assets_dir, theme=pdf_theme)
    else:
        raise ValueError(f'Unsupported format: {fmt}')
