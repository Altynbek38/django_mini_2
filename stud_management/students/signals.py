from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Student

@receiver(post_save, sender=Student)
@receiver(post_delete, sender=Student)
def claer_course_cache(sender, **kwargs):
    cache_keys = cache.keys("student:*")

    for key in cache_keys:
        cache.delete(key)