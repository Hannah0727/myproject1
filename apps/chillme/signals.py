from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Event
from .views import advance_event_list_cache_version


@receiver(post_save, sender=Event)
def invalidate_event_list_cache_after_creation(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(advance_event_list_cache_version)
