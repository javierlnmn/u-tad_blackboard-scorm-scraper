from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str
    viewport_width: int
    viewport_height: int
    output_path: str


def load_settings() -> Settings:
    """Build settings from environment variables."""
    import os
    from os.path import dirname, join

    from dotenv import load_dotenv

    load_dotenv(join(dirname(__file__), '..', '.env'))

    return Settings(
        base_url=os.getenv('BLACKBOARD_URL', 'https://u-tad.blackboard.com/').strip() or '',
        viewport_width=int(os.getenv('VIEWPORT_WIDTH', '1920')),
        viewport_height=int(os.getenv('VIEWPORT_HEIGHT', '1080')),
        output_path=os.getenv('OUTPUT_PATH', 'curso.txt'),
    )
