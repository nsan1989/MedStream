from django import template
from core.menu import MENU_ITEMS

register = template.Library()


@register.simple_tag
def get_menu_items():
    return MENU_ITEMS
