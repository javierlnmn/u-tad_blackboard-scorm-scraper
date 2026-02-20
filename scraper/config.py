from __future__ import annotations

from enum import Enum


class OutputFormat(Enum):
    MD = ('md', 'Markdown')
    PDF = ('pdf', 'PDF')

    @property
    def extension(self) -> str:
        return self.value[0]

    @classmethod
    def from_extension(cls, ext: str) -> OutputFormat:
        ext = (ext or '').lower().strip() or 'md'
        for f in cls:
            if f.value[0] == ext:
                return f
        raise ValueError(f'Unknown output format: {ext!r}')


DEFAULT_BASE_URL = 'https://u-tad.blackboard.com/'
DEFAULT_VIEWPORT_WIDTH = 1440
DEFAULT_VIEWPORT_HEIGHT = 900
DEFAULT_COURSE_NAME = 'course'
DEFAULT_OUTPUT_FORMAT = OutputFormat.MD


class Config:
    def __init__(self) -> None:
        self.base_url = DEFAULT_BASE_URL
        self.viewport_width = DEFAULT_VIEWPORT_WIDTH
        self.viewport_height = DEFAULT_VIEWPORT_HEIGHT
        self.course_name = DEFAULT_COURSE_NAME
        self.output_format = DEFAULT_OUTPUT_FORMAT
        self.output_path = f'./output/{self.course_name}'


_CONFIG = Config()


def get_config() -> Config:
    return _CONFIG
