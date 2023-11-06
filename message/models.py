from django.db import models

from channel.models import Channel


class Message(models.Model):
    tg_message_id = models.BigIntegerField(verbose_name='ID в телеграмме', null=False, blank=False, default=1)
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

    average_reaction_coef = models.DecimalField(  # message.reaction / message.views
        verbose_name='Коэффициент реакций',
        help_text='Текущий коэффициент',
        max_digits=5,
        decimal_places=2,
        default=1
    )
    average_forward_coef = models.DecimalField(  # message.forward / message.views
        verbose_name='Коэффициент репостов',
        help_text='Текущий коэффициент',
        max_digits=5,
        decimal_places=2,
        default=1
    )
    is_forwarded = models.BooleanField(
        verbose_name='Переслан?',
        default=False
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        unique_together = ['channel', 'tg_message_id']

    def __str__(self):
        return f"{self.channel}: message_id: {self.pk}"
