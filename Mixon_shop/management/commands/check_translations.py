"""Ищет в базе тексты, из-за которых на сайте смешаются языки.

    python manage.py check_translations

Для каждого переводимого поля (modeltranslation) сообщает:
- заполнен только один язык: на другой версии сайта покажется текст первого;
- в украинском поле русские буквы (ы, э, ъ, ё) или в русском украинские (і, ї, є, ґ);
- украинский и русский тексты одинаковые (часто это значит, что перевод не вписан).
"""
import re

from django.core.management.base import BaseCommand
from modeltranslation.translator import translator

UK_ONLY = re.compile(r"[ІіЇїЄєҐґ]")
RU_ONLY = re.compile(r"[ЫыЭэЪъЁё]")
LETTERS = re.compile(r"[А-Яа-яІіЇїЄєҐґЁё]{3,}")


def problems(uk, ru):
    uk, ru = (uk or '').strip(), (ru or '').strip()
    if not uk and not ru:
        return []
    if not uk:
        return ['нет украинского текста']
    if not ru:
        return ['нет русского текста']
    found = []
    if RU_ONLY.search(uk):
        found.append('в украинском тексте русские буквы')
    if UK_ONLY.search(ru):
        found.append('в русском тексте украинские буквы')
    if uk == ru and LETTERS.search(uk):
        found.append('тексты на обоих языках одинаковые')
    return found


class Command(BaseCommand):
    help = 'Проверить переводы в базе: пустые, перепутанные и одинаковые uk/ru тексты.'

    def handle(self, *args, **options):
        total = 0
        for model in translator.get_registered_models(abstract=False):
            fields = sorted(translator.get_options_for_model(model).fields)
            for obj in model._default_manager.all().order_by('pk'):
                for field in fields:
                    for problem in problems(getattr(obj, f'{field}_uk'), getattr(obj, f'{field}_ru')):
                        total += 1
                        self.stdout.write(f'{model._meta.verbose_name} #{obj.pk} «{obj}», '
                                          f'поле {field}: {problem}')
        if total:
            self.stdout.write(self.style.WARNING(f'Найдено проблем: {total}. Исправьте их в админке.'))
        else:
            self.stdout.write(self.style.SUCCESS('Все переводы в базе заполнены.'))
