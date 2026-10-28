from modeltranslation.translator import TranslationOptions, translator

from .models import (
    BindingSubstance, Branch, Category, Characteristic, City, ContentBlock, MainPageBanner, News,
    NewsCategory, OrderStatus, PaymentMethod, Product, ProductCharacteristic, ProductParameter,
    ProductTableRow, ProductType, Region, ShipmentMethod,
)


def both_languages(*fields):
    """Поля, которые в админке обязательно заполнять и на украинском, и на русском:
    пустое русское поле на сайте подменилось бы украинским, и языки смешались бы."""
    return {'uk': fields, 'ru': fields}


class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'usage', 'table_title')
    required_languages = both_languages('name')


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = both_languages('name')


class ProductTypeTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = both_languages('name')


class BindingSubstanceTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = both_languages('name')


class NewsCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = both_languages('name')


class NewsTranslationOptions(TranslationOptions):
    fields = ('title',)
    required_languages = both_languages('title')


class ContentBlockTranslationOptions(TranslationOptions):
    fields = ('text',)


translator.register(Product, ProductTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(ProductType, ProductTypeTranslationOptions)
translator.register(BindingSubstance, BindingSubstanceTranslationOptions)
translator.register(NewsCategory, NewsCategoryTranslationOptions)
translator.register(News, NewsTranslationOptions)
translator.register(ContentBlock, ContentBlockTranslationOptions)


class CharacteristicTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = both_languages('name')


class ProductCharacteristicTranslationOptions(TranslationOptions):
    fields = ('value',)


translator.register(Characteristic, CharacteristicTranslationOptions)
translator.register(ProductCharacteristic, ProductCharacteristicTranslationOptions)


class ProductParameterTranslationOptions(TranslationOptions):
    fields = ('name', 'unit')
    required_languages = both_languages('name')


translator.register(ProductParameter, ProductParameterTranslationOptions)


# Справочники, которые видит покупатель: города и области в формах, адреса филиалов,
# статус заказа и способы доставки/оплаты в кабинете, баннеры главной, строки таблицы
# вариантов на странице товара (названия цветов).
class NameTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = both_languages('name')


class BranchTranslationOptions(TranslationOptions):
    fields = ('address_base', 'address_detail', 'address_short')
    required_languages = both_languages('address_short')


class MainPageBannerTranslationOptions(TranslationOptions):
    fields = ('description',)
    required_languages = both_languages('description')


for model in (Region, City, OrderStatus, ShipmentMethod, PaymentMethod, ProductTableRow):
    translator.register(model, NameTranslationOptions)
translator.register(Branch, BranchTranslationOptions)
translator.register(MainPageBanner, MainPageBannerTranslationOptions)
