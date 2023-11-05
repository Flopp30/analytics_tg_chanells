from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models


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
    max_forward_coef = models.DecimalField(
        verbose_name="Коэффициент репостов",
        help_text='Коэффициент, выше которого репостим сообщение',
        max_digits=5,
        decimal_places=2,
        default=10
    )
    max_reaction_coef = models.DecimalField(
        verbose_name="Коэффициент реакций",
        help_text='Коэффициент, выше которого репостим сообщение',
        max_digits=5,
        decimal_places=2,
        default=10
    )

    additional_percents_for_repost = models.DecimalField(
        verbose_name='Процент превышения',
        help_text='Процент превышения, при котором репостим (%)',
        max_digits=5,
        decimal_places=2,
        default=30
    )

    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return f'Настройки'


ext_settings, _ = ExternalSettings.objects.get_or_create(pk=1)
settings.MAX_FORWARD_COEF = ext_settings.max_forward_coef
settings.MAX_REACTION_COEF = ext_settings.max_reaction_coef
settings.ADDITIONAL_PERCENTS_FOR_REPOST = ext_settings.additional_percents_for_repost
