from __future__ import annotations

from pathlib import Path

from scraper.config import OutputFormat
from scraper.formats.base import CourseWriter
from scraper.utils.links import slugify

from .builder import MarkdownBuilder


class MDWriter(CourseWriter):
    def write(
        self,
        course,
        output_path: Path,
        assets_dir: Path,
    ) -> None:
        builder = MarkdownBuilder(output_path=output_path)

        builder.add_elements(builder.build_heading(1, course.title))
        builder.add_elements(builder.build_spacer())

        # Index
        index_entries: list[tuple[int, str]] = []
        for section_idx, section in enumerate(course.sections, start=1):
            index_entries.append((2, f'{section_idx}. {section.title}'.strip()))
            for lesson_idx, lesson in enumerate(section.lessons, start=1):
                index_entries.append((3, f'{section_idx}.{lesson_idx} {lesson.title}'.strip()))

        if index_entries:
            used: dict[str, int] = {}
            lines = [builder.build_heading(2, 'Index'), '']
            for level, heading in index_entries:
                base = slugify(heading)
                n = used.get(base, 0)
                used[base] = n + 1
                anchor = base if n == 0 else f'{base}-{n + 1}'
                indent = '  ' * max(0, level - 2)
                lines.append(f'{indent}- [{heading}](#{anchor})')
            lines.append('')
            builder.add_elements('\n'.join(lines).strip())
            builder.add_elements(builder.build_spacer())

        # Content
        for section_idx, section in enumerate(course.sections, start=1):
            builder.add_elements(builder.build_heading(2, f'{section_idx}. {section.title}'))
            builder.add_elements(builder.build_spacer())

            for lesson_idx, lesson in enumerate(section.lessons, start=1):
                builder.add_elements(builder.build_heading(3, f'{section_idx}.{lesson_idx} {lesson.title}'))
                builder.add_elements(builder.build_spacer())

                for block in lesson.blocks:
                    rendered = block.render(fmt=OutputFormat.MD, assets_dir=assets_dir)
                    if rendered:
                        builder.add_elements(rendered.strip())
                        builder.add_elements(builder.build_spacer())

        builder.build()
