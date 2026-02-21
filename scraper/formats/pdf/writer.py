"""Write course content to PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import inch

from .builder import PDFBuilder


def write_course(course, output_path: Path, *, assets_dir: Path, theme: str | None = None) -> None:
    """Write course as PDF."""
    from .themes import ThemeRegistry

    pdf_theme = ThemeRegistry.from_name(theme or 'ocean').get_theme()
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
                lesson_flowables.extend(block._render_pdf(builder, assets_dir=assets_dir))

            builder.add_elements(lesson_flowables)

        builder.add_elements(builder.build_spacer(0.08 * inch))

    builder.build()
