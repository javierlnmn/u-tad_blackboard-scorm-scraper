from bs4 import BeautifulSoup

from scraper.models.course_scheme import CourseSchemeLesson, CourseSchemeSection

SIDEBAR_SECTION_TITLE_CLASS = 'nav-sidebar__outline-section-toggle-text'
SIDEBAR_LESSON_LINKS_CLASS = 'a.nav-sidebar__outline-section-item__link'

SIDEBAR_LESSON_LINKS_SELECTOR = f'#nav-content-sidebar {SIDEBAR_LESSON_LINKS_CLASS}'


def _lesson_id_from_href(href: str | None) -> str | None:
    if not href:
        return None
    marker = '#/lessons/'
    if marker in href:
        return href.split(marker, 1)[1] or None
    return None


def parse_sidebar(html: str) -> list[CourseSchemeSection]:
    soup = BeautifulSoup(html, 'html.parser')
    sidebar = soup.select_one('#nav-content-sidebar')
    if not sidebar:
        return []

    global_lesson_index = 0
    sections: list[CourseSchemeSection] = []

    for section_li in sidebar.select('li.nav-sidebar__outline-section'):
        title_el = section_li.select_one(f'.{SIDEBAR_SECTION_TITLE_CLASS}')
        section_title = (title_el.get_text(strip=True) if title_el else '') or 'Lessons'

        lessons: list[CourseSchemeLesson] = []
        for a in section_li.select(SIDEBAR_LESSON_LINKS_CLASS):
            title = a.get_text(strip=True)
            if not title:
                continue

            href = a.get('href')
            lessons.append(
                CourseSchemeLesson(
                    index=global_lesson_index,
                    title=title,
                    href=href,
                    lesson_id=_lesson_id_from_href(href),
                )
            )
            global_lesson_index += 1

        if lessons:
            sections.append(CourseSchemeSection(title=section_title.title().strip(), lessons=lessons))

    if not sections:
        lessons: list[CourseSchemeLesson] = []
        for a in sidebar.select(SIDEBAR_LESSON_LINKS_CLASS):
            title = a.get_text(strip=True)
            if not title:
                continue
            href = a.get('href')
            lessons.append(
                CourseSchemeLesson(
                    index=global_lesson_index,
                    title=title.title().strip(),
                    href=href,
                    lesson_id=_lesson_id_from_href(href),
                )
            )
            global_lesson_index += 1
        if lessons:
            return [CourseSchemeSection(title='Lessons', lessons=lessons)]

    return sections
