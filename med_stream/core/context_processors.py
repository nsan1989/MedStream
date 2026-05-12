from core.menu import MENU_ITEMS, SIDEBAR_TOP_ITEMS


def menu_items(request):
    return {
        "menu_items": MENU_ITEMS,
        "sidebar_top_items": SIDEBAR_TOP_ITEMS,
    }
