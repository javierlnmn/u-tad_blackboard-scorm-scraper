from __future__ import annotations

DEFAULT_BASE_URL = 'https://u-tad.blackboard.com/'
DEFAULT_VIEWPORT_WIDTH = 1920
DEFAULT_VIEWPORT_HEIGHT = 1080
DEFAULT_COURSE_NAME = 'course'
DEFAULT_OUTPUT_FORMAT = 'md'


class Config:
    def __init__(self) -> None:
        self.base_url = DEFAULT_BASE_URL
        self.viewport_width = DEFAULT_VIEWPORT_WIDTH
        self.viewport_height = DEFAULT_VIEWPORT_HEIGHT
        self.course_name = DEFAULT_COURSE_NAME
        self.output_format = DEFAULT_OUTPUT_FORMAT  # "md" | "pdf" | "txt"
        self.output_path = f'./output/{self.course_name}.{self.output_format}'


_CONFIG = Config()


def get_config() -> Config:
    return _CONFIG
