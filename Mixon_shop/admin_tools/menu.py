from admin_tools.menu import items, Menu
from django.urls import reverse

from .groups import GROUPS


class CustomMenu(Menu):
    def init_with_context(self, context):
        self.children += [items.MenuItem('Главная', reverse('admin:index'))]
        self.children += [
            items.MenuItem(title, children=[items.ModelList(title, models=models)])
            for title, models in GROUPS
        ]
        self.children += [items.MenuItem('Открыть сайт', reverse('home'))]
