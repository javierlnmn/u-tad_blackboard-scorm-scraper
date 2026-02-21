from __future__ import annotations

import re

from scraper.config import Config, OutputFormat, get_config
from scraper.formats.pdf import ThemeRegistry


def _prompt(text: str, default: str) -> str:
    raw = input(f'{text} [{default}]: ').strip()
    return raw or default


def _prompt_menu(title: str, options: list[tuple[str, str]], default_id: str) -> str:
    print(title)
    default_index = 0
    for i, (opt_id, label) in enumerate(options, start=1):
        if opt_id == default_id:
            default_index = i
        print(f'  {i}) {label}')
    raw = input(f'Select option [{default_index}]: ').strip()
    if not raw:
        return default_id
    try:
        idx = int(raw)
    except ValueError:
        return default_id
    if 1 <= idx <= len(options):
        return options[idx - 1][0]
    return default_id


def _normalize_course_name(raw: str) -> str:
    name = (raw or '').strip() or 'course'
    name = re.sub(r'\s+', ' ', name).strip()
    name = name.replace('/', '-').replace('\\', '-')
    return name


def run_setup_wizard() -> Config:
    current = get_config()

    print('\nBlackboard SCORM Scraper setup\n')

    course_name = _normalize_course_name(_prompt('Course name', current.course_name))
    base_url = _prompt('Blackboard URL', current.base_url)

    output_format_raw = _prompt_menu(
        'Output format:',
        options=[(f.extension, f'{f.value[1]} (.{f.extension})') for f in OutputFormat],
        default_id=current.output_format.extension
        if isinstance(current.output_format, OutputFormat)
        else (current.output_format or OutputFormat.MD.extension),
    )
    output_format = OutputFormat.from_extension(output_format_raw)

    pdf_theme = current.pdf_theme
    if output_format == OutputFormat.PDF:
        theme_options = [(t, t.capitalize()) for t in ThemeRegistry.list_themes()]
        pdf_theme = _prompt_menu(
            'PDF theme:',
            options=theme_options,
            default_id=current.pdf_theme if current.pdf_theme in {t for t, _ in theme_options} else 'ocean',
        )

    default_output_dir = f'./output/{course_name}'
    output_path = _prompt('Output folder', default_output_dir)

    if '/' not in output_path and '\\' not in output_path and not output_path.startswith('.'):
        output_path = f'./output/{output_path}'

    current.base_url = base_url
    current.course_name = course_name
    current.output_format = output_format
    current.pdf_theme = pdf_theme
    current.output_path = output_path or f'./output/{course_name}'
    print('\nConfig set for this run.\n')
    return current
