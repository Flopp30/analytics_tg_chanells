from django.conf import settings
from django.db import models


class Channel(models.Model):
    name = models.CharField(
        verbose_name='Название канала',
        max_length=128,
        default='No name channel',
    )
    category = models.CharField(
        verbose_name='Категория канала',
        help_text='Для фильтрации',
        max_length=128,
        default='Без категории'
    )
    max_react_coef = models.DecimalField(
        verbose_name='Коэффициент, когда репостим по реакциям',
        help_text='Если он None - берется из настроек',
        decimal_places=2,
        max_digits=5,
        default=None,
        null=True,
        blank=True,
    )
    max_forward_coef = models.DecimalField(
        verbose_name='Коэффициент, когда репостим по репостам',
        help_text='Если он None - берется из настроек',
        decimal_places=2,
        max_digits=5,
        default=None,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Канал'
        verbose_name_plural = 'Каналы'

    def __str__(self):
        return f"{self.pk}: {self.name}"
