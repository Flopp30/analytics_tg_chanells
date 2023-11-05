from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from bot_parts.models import ExternalSettings


@receiver(post_save, sender=ExternalSettings)
def update_settings(sender, instance, **kwargs):
    for key, value in instance.__dict__.items():
        if key != 'id' and not key.startswith('_'):
            setattr(settings, key.upper(), value)
