from __future__ import annotations

from pathlib import Path

from scraper.config import OutputFormat
from scraper.formats.base import CourseWriter
from scraper.utils.links import slugify


class MDWriter(CourseWriter):
    def write(
        self,
        course,
        output_path: Path,
        *,
        assets_dir: Path,
        **kwargs: object,
    ) -> None:
        chunks: list[str] = []
        chunks.append(f'# {course.title}'.strip())
        chunks.append('')

        index_entries: list[tuple[int, str]] = []
        for section_idx, section in enumerate(course.sections, start=1):
            index_entries.append((2, f'{section_idx}. {section.title}'.strip()))
            for lesson_idx, lesson in enumerate(section.lessons, start=1):
                index_entries.append((3, f'{section_idx}.{lesson_idx} {lesson.title}'.strip()))

        if index_entries:
            used: dict[str, int] = {}
            lines = ['## Index', '']
            for level, heading in index_entries:
                base = slugify(heading)
                n = used.get(base, 0)
                used[base] = n + 1
                anchor = base if n == 0 else f'{base}-{n + 1}'
                indent = '  ' * max(0, level - 2)
                lines.append(f'{indent}- [{heading}](#{anchor})')
            lines.append('')
            chunks.append('\n'.join(lines).strip())
            chunks.append('')

        for section_idx, section in enumerate(course.sections, start=1):
            chunks.append(f'## {section_idx}. {section.title}'.strip())
            chunks.append('')

            for lesson_idx, lesson in enumerate(section.lessons, start=1):
                chunks.append(f'### {section_idx}.{lesson_idx} {lesson.title}'.strip())
                chunks.append('')

                for block in lesson.blocks:
                    rendered = block.render(fmt=OutputFormat.MD, assets_dir=assets_dir).strip()
                    if rendered:
                        chunks.append(rendered)
                        chunks.append('')

        content = '\n\n'.join(c for c in chunks if c is not None).rstrip() + '\n'
        output_path.write_text(content, encoding='utf-8')
