from bs4 import BeautifulSoup

from scraper.models import SidebarItem

SIDEBAR_LESSON_LINKS_CLASS = 'a.nav-sidebar__outline-section-item__link'
SIDEBAR_LESSON_LINKS_SELECTOR = f'#nav-content-sidebar {SIDEBAR_LESSON_LINKS_CLASS}'


def parse_sidebar(html: str) -> list[SidebarItem]:
    """
    Parse the sidebar HTML and return lesson items in document order.

    Expects #nav-content-sidebar with outline sections; each lesson is an
    <a class="nav-sidebar__outline-section-item__link" data-link="lesson-link-item">.
    """
    soup = BeautifulSoup(html, 'html.parser')
    sidebar = soup.select_one('#nav-content-sidebar')
    if not sidebar:
        return []

    items: list[SidebarItem] = []
    for i, a in enumerate(sidebar.select(SIDEBAR_LESSON_LINKS_CLASS)):
        label = a.get_text(strip=True)
        if not label:
            continue
        items.append(
            SidebarItem(
                index=i,
                label=label,
                href=a.get('href'),
            )
        )
    return items
