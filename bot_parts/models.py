from django.conf import settings
from django.core.exceptions import ValidationError
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
        decimal_places=2,
        default=30
    )
    starting_interval_second_task = models.IntegerField(
        verbose_name='Интервал запуска второй задачи',
        help_text='В минутах',
        choices=interval_choices,
        default=5
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
except OperationalError:
    pass
