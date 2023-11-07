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
    reaction_coef = models.DecimalField(verbose_name='Коэффициент реакций', max_digits=10, decimal_places=2, default=0)
    forwards_coef = models.DecimalField(verbose_name='Коэффициент репостов', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Метрика'
        verbose_name_plural = 'Метрики'

    def update_from_message(self, message: Message):
        self.views = message.views
        self.forwards = message.forwards
        self.reactions = message.reactions
        self.reaction_coef = self.reactions / self.views if self.views != 0 else 0
        self.forwards_coef = self.forwards / self.views if self.views != 0 else 0
        self.message = message
