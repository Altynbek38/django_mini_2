from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Course

@receiver(post_save, sender=Course)
@receiver(post_delete, sender=Course)
def claer_course_cache(sender, **kwargs):
    cache_keys = cache.keys("courses:list:*")

    for key in cache_keys:
        cache.delete(key)