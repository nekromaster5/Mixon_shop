from modeltranslation.translator import TranslationOptions, translator

from .models import (
    BindingSubstance, Category, Characteristic, ContentBlock, News, NewsCategory, Product,
    ProductCharacteristic, ProductParameter, ProductType,
)


class ProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'usage', 'table_title')


class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


class ProductTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


class BindingSubstanceTranslationOptions(TranslationOptions):
    fields = ('name',)


class NewsCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


class NewsTranslationOptions(TranslationOptions):
    fields = ('title',)


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


class ProductCharacteristicTranslationOptions(TranslationOptions):
    fields = ('value',)


translator.register(Characteristic, CharacteristicTranslationOptions)
translator.register(ProductCharacteristic, ProductCharacteristicTranslationOptions)


class ProductParameterTranslationOptions(TranslationOptions):
    fields = ('name', 'unit')


translator.register(ProductParameter, ProductParameterTranslationOptions)
