from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard


class CustomIndexDashboard(Dashboard):
    def init_with_context(self, context):
        self.children.append(modules.ModelList(
            title='Пользователи и профили',
            models=('django.contrib.auth.models.User', 'Mixon_shop.models.FavoriteProduct',
                    'Mixon_shop.models.ProductComparison',
                    'Mixon_shop.models.Review', 'Mixon_shop.models.Region'),
            collapsible=True,
            collapsed=False,
        ))

        self.children.append(modules.ModelList(
            title='Управление товарами',
            models=('Mixon_shop.models.Product', 'Mixon_shop.models.ProductStock',
                    'Mixon_shop.models.Color', 'Mixon_shop.models.Volume',
                    'Mixon_shop.models.BindingSubstance', 'Mixon_shop.models.ProductType',
                    'Mixon_shop.models.PromoCode',)
        ))

        self.children.append(modules.ModelList(
            title='Новости',
            models=('Mixon_shop.models.News', 'Mixon_shop.models.NewsCategory')
        ))

        self.children.append(modules.ModelList(
            title='Заказы и статус',
            models=('Mixon_shop.models.Order', 'Mixon_shop.models.OrderStatus')
        ))

        self.children.append(modules.ModelList(
            title='Местоположения и филиалы',
            models=('Mixon_shop.models.Branch', 'Mixon_shop.models.City', 'Mixon_shop.models.PhoneNumber')
        ))

        self.children.append(modules.ModelList(
            title='Сообщения и уведомления',
            models=('Mixon_shop.models.ErrorMessages', 'Mixon_shop.models.InfoMessages')
        ))




class CustomAppIndexDashboard(AppIndexDashboard):
    def init_with_context(self, context):
        self.children.append(modules.ModelList(
            title=self.app_title,
            models=self.models,
        ))
