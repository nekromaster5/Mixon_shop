from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from django.urls import reverse

from .groups import COLLAPSED, GROUPS


class CustomIndexDashboard(Dashboard):
    columns = 2

    def init_with_context(self, context):
        self.children.append(modules.LinkList(
            title='Быстрые действия',
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                ['Заказы', reverse('admin:Mixon_shop_order_changelist')],
                ['Необработанные заявки',
                 reverse('admin:Mixon_shop_productrequest_changelist') + '?is_processed__exact=0'],
                ['Добавить товар', reverse('admin:Mixon_shop_product_add')],
                ['Товары без наличия', reverse('admin:Mixon_shop_product_changelist') + '?is_in_stock__exact=0'],
                ['Открыть сайт', reverse('home')],
            ],
        ))

        for title, models in GROUPS:
            self.children.append(modules.ModelList(
                title=title,
                models=models,
                collapsible=True,
                collapsed=title in COLLAPSED,
            ))

        self.children.append(modules.RecentActions(title='Последние изменения', limit=10))


class CustomAppIndexDashboard(AppIndexDashboard):
    def init_with_context(self, context):
        self.children.append(modules.ModelList(
            title=self.app_title,
            models=self.models,
        ))
