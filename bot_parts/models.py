from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, OperationalError


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def delete(self, *args, **kwargs):
        raise ValidationError("Вы не можете удалить этот объект")


class ExternalSettings(SingletonModel):
    interval_choices = ((5, 5), (10, 10))
    additional_percents_for_repost = models.DecimalField(
        verbose_name='Процент превышения',
        help_text='Процент превышения, при котором репостим (%)',
        max_digits=5,
        decimal_places=5,
        default=30
    )
    starting_interval_second_task = models.IntegerField(
        verbose_name='Интервал запуска второй задачи',
        help_text='В минутах',
        choices=interval_choices,
        default=5
    )
    min_messages_count_before_repost = models.IntegerField(
        verbose_name='Минимальное количество сообщений',
        help_text='Минимальное количество сообщений в канале до отправки репоста',
        default=20
    )
    min_metrics_count_before_repost = models.IntegerField(
        verbose_name='Количество метрик',
        help_text='Количество метрик у сообщения до отправки репоста',
        default=5
    )
    messages_ttl = models.IntegerField(
        verbose_name='Длительность хранения сообщений',
        help_text='В днях, метрики удаляются вместе. 0 - не удалять вообще никакие сообщения.',
        default=30
    )

    views_div = models.IntegerField(
        verbose_name='Знаменатель для просмотров в формуле',
        help_text='rection coef = reactions / (views / знаменатель)',
        default=100,
        validators=[MinValueValidator(0.1, message='Делитель должен быть строго больше 0')]
    )

    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return f'Настройки'


try:
    ext_settings, _ = ExternalSettings.objects.get_or_create(pk=1)
    for key, value in ext_settings.__dict__.items():
        if key != 'id' and not key.startswith('_'):
            setattr(settings, key.upper(), value)
except Exception:
    pass
