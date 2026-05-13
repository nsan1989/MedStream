from core.menu import MENU_ITEMS


def menu_items(request):
    menu_items = []

    if request.user.is_authenticated:
        role = request.user.role

        menu_items = MENU_ITEMS.get(role, [])

    return {"menu_items": menu_items}
