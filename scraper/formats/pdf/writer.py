from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch

from scraper.config import OutputFormat
from scraper.formats.base import CourseWriter
from scraper.utils.links import slugify

from .builder import PDFBuilder
from .themes import PDFTheme, ThemeRegistry


def _make_anchor(heading: str, used: dict[str, int]) -> str:
    base = slugify(heading)
    n = used.get(base, 0)
    used[base] = n + 1
    return base if n == 0 else f'{base}-{n + 1}'


class PDFWriter(CourseWriter):
    def __init__(self, theme: PDFTheme = ThemeRegistry.from_name('ocean').get_theme()) -> None:
        self.theme = theme

    def write(
        self,
        course,
        output_path: Path,
        assets_dir: Path,
    ) -> None:
        builder = PDFBuilder(output_path=output_path, theme=self.theme)
        builder.add_elements(builder.build_title(course.title))
        builder.add_elements(builder.build_spacer(0.1 * inch))

        # Index
        used: dict[str, int] = {}
        index_entries: list[tuple[int, str, str]] = []
        for section_idx, section in enumerate(course.sections, start=1):
            section_heading = f'{section_idx}. {section.title}'.strip()
            index_entries.append((2, section_heading, _make_anchor(section_heading, used)))
            for lesson_idx, lesson in enumerate(section.lessons, start=1):
                lesson_heading = f'{section_idx}.{lesson_idx} {lesson.title}'.strip()
                index_entries.append((3, lesson_heading, _make_anchor(lesson_heading, used)))

        if index_entries:
            builder.add_elements(builder.build_heading('Index'))
            builder.add_elements(builder.build_spacer(0.06 * inch))
            indent_pt_per_level = 18
            for level, heading, anchor in index_entries:
                indent_pt = indent_pt_per_level * max(0, level - 2)
                builder.add_elements(builder.build_index_link(heading, anchor, indent_pt=indent_pt))
            builder.add_elements(builder.build_spacer(0.15 * inch))

        # Content
        builder.add_elements(builder.build_page_break())
        for section_idx, section in enumerate(course.sections, start=1):
            if section_idx > 1:
                builder.add_elements(builder.build_page_break())
            section_heading = f'{section_idx}. {section.title}'
            section_anchor = next(a for _, h, a in index_entries if h == section_heading.strip())
            builder.add_elements(builder.build_heading(section_heading, anchor=section_anchor))
            builder.add_elements(builder.build_spacer(0.06 * inch))

            for lesson_idx, lesson in enumerate(section.lessons, start=1):
                lesson_heading = f'{section_idx}.{lesson_idx} {lesson.title}'
                lesson_anchor = next(a for _, h, a in index_entries if h == lesson_heading.strip())
                lesson_flowables = builder.build_subheading(lesson_heading, anchor=lesson_anchor)

                for block in lesson.blocks:
                    flowables = block.render(fmt=OutputFormat.PDF, builder=builder, assets_dir=assets_dir)
                    if flowables:
                        lesson_flowables.extend(flowables)

                builder.add_elements(lesson_flowables)

            builder.add_elements(builder.build_spacer(0.08 * inch))

        builder.build()
