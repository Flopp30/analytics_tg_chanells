from django.db import models

from message.models import Message


class Metric(models.Model):
    views = models.BigIntegerField(verbose_name='Просмотры', default=0)
    reactions = models.BigIntegerField(verbose_name='Реакции', default=0)
    forwards = models.BigIntegerField(verbose_name='Репосты', default=0)
    message = models.ForeignKey(
        Message,
        verbose_name='Сообщение',
        related_name='metrics',
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Метрика'
        verbose_name_plural = 'Метрики'
