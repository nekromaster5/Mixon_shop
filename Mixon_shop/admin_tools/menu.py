from admin_tools.menu import items, Menu


class CustomMenu(Menu):
    def init_with_context(self, context):
        self.children += [
            items.MenuItem('Пользователи и профили', children=[
                items.ModelList(
                    'Пользователи и профили',
                    models=('django.contrib.auth.models.User', 'Mixon_shop.models.FavoriteProduct',
                            'Mixon_shop.models.ProductComparison', 'Mixon_shop.models.Review',
                            'Mixon_shop.models.Region')
                ),
            ]),
            items.MenuItem('Управление товарами', children=[
                items.ModelList(
                    'Управление товарами',
                    models=('Mixon_shop.models.Product', 'Mixon_shop.models.ProductStock',
                            'Mixon_shop.models.Color', 'Mixon_shop.models.Volume',
                            'Mixon_shop.models.BindingSubstance', 'Mixon_shop.models.ProductType',)
                ),
            ]),
            items.MenuItem('Продукты и категории', children=[
                items.ModelList(
                    'Продукты и категории',
                    models=('Mixon_shop.models.News', 'Mixon_shop.models.NewsCategory')
                ),
            ]),
            items.MenuItem('Заказы и статус', children=[
                items.ModelList(
                    'Заказы и статус',
                    models=('Mixon_shop.models.Order', 'Mixon_shop.models.OrderStatus')
                ),
            ]),
            items.MenuItem('Местоположения и филиалы', children=[
                items.ModelList(
                    'Местоположения и филиалы',
                    models=('Mixon_shop.models.Branch', 'Mixon_shop.models.City', 'Mixon_shop.models.PhoneNumber')
                ),
            ]),
            items.MenuItem('Сообщения и уведомления', children=[
                items.ModelList(
                    'Сообщения и уведомления',
                    models=('Mixon_shop.models.ErrorMessages', 'Mixon_shop.models.InfoMessages')
                ),
            ]),
        ]
