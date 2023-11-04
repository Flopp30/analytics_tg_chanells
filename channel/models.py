from django.db import models


class Channel(models.Model):
    name = models.CharField(
        verbose_name='Название канала',
        max_length=128,
        default='No name channel',
    )
    category = models.CharField(
        verbose_name='Категория чата',
        max_length=128,
        default='Без категории'
    )
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Канал'
        verbose_name_plural = 'Каналы'

    def __str__(self):
        return f"{self.pk}: {self.name}"
