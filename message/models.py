from django.db import models

from channel.models import Channel


class Message(models.Model):
    text = models.TextField(verbose_name='Текст сообщения', default='Empty')
    views = models.BigIntegerField(verbose_name='Просмотры', default=0)
    reactions = models.BigIntegerField(verbose_name='Реакции', default=0)
    forwards = models.BigIntegerField(verbose_name='Репосты', default=0)
    channel = models.ForeignKey(
        Channel,
        verbose_name='Канал',
        related_name='messages',
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлен', auto_now=True)

    current_reaction_coef = models.DecimalField(  # message.reaction / message.views
        verbose_name='Коэффициент реакций',
        help_text='Текущий коэффициент',
        max_digits=5,
        decimal_places=2,
        default=1
    )
    current_forward_coef = models.DecimalField(  # message.forward / message.views
        verbose_name='Коэффициент репостов',
        help_text='Текущий коэффициент',
        max_digits=5,
        decimal_places=2,
        default=1
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f"{self.channel}: message_id: {self.pk}"
