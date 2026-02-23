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


def _parse_range(s: str, n: int) -> list[int]:
    """Parse '1', '1-3', '1, 3', '1 2' into sorted unique indices in 1..n."""
    seen: set[int] = set()
    for part in re.split(r'[,\s]+', s):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            lo, _, hi = part.partition('-')
            try:
                a, b = int(lo.strip()), int(hi.strip())
                for i in range(min(a, b), max(a, b) + 1):
                    if 1 <= i <= n:
                        seen.add(i)
            except ValueError:
                pass
        else:
            try:
                i = int(part)
                if 1 <= i <= n:
                    seen.add(i)
            except ValueError:
                pass
    return sorted(seen)


def _prompt_multi_select(
    title: str,
    options: list[tuple[str, str]],
    default_ids: list[str],
) -> list[str]:
    """Prompt for multiple options. Accepts: 1, 1 2, 1-3, 1, 3-4, etc."""
    print(title)
    for i, (opt_id, label) in enumerate(options, start=1):
        print(f'  {i}) {label}')
    default_indices = [i for i, (oid, _) in enumerate(options, start=1) if oid in default_ids]
    default_str = ','.join(str(i) for i in default_indices) if default_indices else '1'
    raw = input(f'Select (e.g. 1, 1 2, 1-3, 1, 3) [{default_str}]: ').strip()
    if not raw:
        raw = default_str
    indices = _parse_range(raw, len(options))
    if not indices:
        return [options[0][0]] if options else []
    return [options[i - 1][0] for i in indices]


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

    format_options = [(f.extension, f'{f.value[1]} (.{f.extension})') for f in OutputFormat]
    default_format_ids = [f.extension for f in current.output_formats]
    selected_extensions = _prompt_multi_select(
        'Output formats:',
        options=format_options,
        default_ids=default_format_ids,
    )
    output_formats = [OutputFormat.from_extension(ext) for ext in selected_extensions]

    pdf_theme = current.pdf_theme
    download_videos = current.download_videos

    if OutputFormat.PDF in output_formats:
        theme_options = [(t, t.capitalize()) for t in ThemeRegistry.list_themes()]
        theme_name = getattr(current.pdf_theme, 'name', 'ocean')
        default_id = theme_name if theme_name in {t for t, _ in theme_options} else 'ocean'
        selected_name = _prompt_menu(
            'PDF theme:',
            options=theme_options,
            default_id=default_id,
        )
        pdf_theme = ThemeRegistry.from_name(selected_name).get_theme()

    if OutputFormat.MD in output_formats:
        raw = input('Download videos? (y/n) [n]: ').strip().lower()
        download_videos = raw in ('y', 'yes')

    default_output_dir = f'./output/{course_name}'
    output_path = _prompt('Output folder', default_output_dir)

    if '/' not in output_path and '\\' not in output_path and not output_path.startswith('.'):
        output_path = f'./output/{output_path}'

    current.base_url = base_url
    current.course_name = course_name
    current.output_formats = output_formats
    current.pdf_theme = pdf_theme
    current.download_videos = download_videos
    current.output_path = output_path or f'./output/{course_name}'
    print('\nConfig set for this run.\n')
    return current
