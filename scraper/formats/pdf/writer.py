from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch

from scraper.config import OutputFormat
from scraper.formats.base import CourseWriter

from .builder import PDFBuilder
from .themes import PDFTheme, ThemeRegistry


class PDFWriter(CourseWriter):
    def __init__(self, theme: PDFTheme = ThemeRegistry.from_name('ocean').get_theme()) -> None:
        self.theme = theme

    def write(
        self,
        course,
        output_path: Path,
        *,
        assets_dir: Path,
        **kwargs: object,
    ) -> None:
        pdf_theme = self.theme
        builder = PDFBuilder(output_path, theme=pdf_theme)
        builder.add_elements(builder.build_title(course.title))
        builder.add_elements(builder.build_spacer(0.1 * inch))

        for section_idx, section in enumerate(course.sections, start=1):
            if section_idx > 1:
                builder.add_elements(builder.build_page_break())
            builder.add_elements(builder.build_heading(f'{section_idx}. {section.title}'))
            builder.add_elements(builder.build_spacer(0.06 * inch))

            for lesson_idx, lesson in enumerate(section.lessons, start=1):
                lesson_flowables = builder.build_subheading(f'{section_idx}.{lesson_idx} {lesson.title}')

                for block in lesson.blocks:
                    flowables = block.render(fmt=OutputFormat.PDF, builder=builder, assets_dir=assets_dir)
                    if flowables:
                        lesson_flowables.extend(flowables)

                builder.add_elements(lesson_flowables)

            builder.add_elements(builder.build_spacer(0.08 * inch))

        builder.build()
