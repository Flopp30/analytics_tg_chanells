from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from bot_parts.models import ExternalSettings


@receiver(post_save, sender=ExternalSettings)
def update_settings(sender, instance, **kwargs):
    settings.MAX_FORWARD_COEF = instance.max_forward_coef
    settings.MAX_REACTION_COEF = instance.max_reaction_coef
