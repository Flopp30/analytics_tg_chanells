from django.db import models


class Category(models.Model):
    target_chat_id = models.CharField(
        verbose_name='Id чата',
        help_text='ID чата, куда отправлять посты, превысившие кап',
        max_length=128
    )
    name = models.CharField(
        verbose_name='Название категории чата',
        max_length=128,
        default='Без названия'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.pk}: {self.name}'


class Channel(models.Model):
    chat_id = models.BigIntegerField('TG ID чата', null=True, blank=True)
    name = models.CharField(
        verbose_name='Название канала',
        max_length=128,
        default='No name channel',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория чата',
        related_name='channels',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    average_react_coef = models.DecimalField(
        verbose_name='Коэффициент, когда репостим по реакциям',
        decimal_places=2,
        max_digits=5,
        default=None,
        null=True,
        blank=True,
    )
    average_forward_coef = models.DecimalField(
        verbose_name='Коэффициент, когда репостим по репостам',
        decimal_places=2,
        max_digits=5,
        default=None,
        null=True,
        blank=True,
    )
    is_tracking = models.BooleanField(
        verbose_name='Отслеживаем?',
        default=False,
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(verbose_name='Создан', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Канал'
        verbose_name_plural = 'Каналы'

    def __str__(self):
        return f"{self.pk}: {self.name}"
