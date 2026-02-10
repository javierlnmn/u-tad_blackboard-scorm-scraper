from bs4 import BeautifulSoup

from scraper.models.sidebar import SidebarItem, SidebarLessonsSection

SIDEBAR_LESSONS_SECTION_TEXT_CLASS = 'nav-sidebar__outline-section-toggle-text'

SIDEBAR_LESSON_LINKS_CLASS = 'a.nav-sidebar__outline-section-item__link'
SIDEBAR_LESSON_LINKS_SELECTOR = f'#nav-content-sidebar {SIDEBAR_LESSON_LINKS_CLASS}'


def parse_sidebar(html: str) -> list[SidebarLessonsSection]:
    soup = BeautifulSoup(html, 'html.parser')
    sidebar = soup.select_one('#nav-content-sidebar')
    if not sidebar:
        return []

    global_lesson_index = 0
    sections: list[SidebarLessonsSection] = []

    for section_li in sidebar.select('li.nav-sidebar__outline-section'):
        title_el = section_li.select_one(f'.{SIDEBAR_LESSONS_SECTION_TEXT_CLASS}')
        section_label = (title_el.get_text(strip=True) if title_el else '') or 'Lessons'

        items: list[SidebarItem] = []
        for a in section_li.select(SIDEBAR_LESSON_LINKS_CLASS):
            label = a.get_text(strip=True)
            if not label:
                continue
            items.append(
                SidebarItem(
                    index=global_lesson_index,
                    label=label,
                    href=a.get('href'),
                )
            )
            global_lesson_index += 1

        if items:
            sections.append(SidebarLessonsSection(label=section_label, items=items))

    if not sections:
        items: list[SidebarItem] = []
        for a in sidebar.select(SIDEBAR_LESSON_LINKS_CLASS):
            label = a.get_text(strip=True)
            if not label:
                continue
            items.append(SidebarItem(index=global_lesson_index, label=label, href=a.get('href')))
            global_lesson_index += 1
        if items:
            return [SidebarLessonsSection(label='Lessons', items=items)]

    return sections
