from django.contrib.auth.signals import user_logged_in, user_logged_out
from djoser.signals import user_registered

from django.dispatch import receiver
import logging

logger = logging.getLogger('user_actions')

@receiver(user_registered)
def log_user_registration(sender, user, request, **kwargs):
    logger.info(f"User registered: {user.email if user.email else user.username}")

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User logged in: {user.email if user.email else user.username}")

@receiver(user_logged_out)
def log_user_logout(sernder, request, user, **kwargs):
    logger.info(f"User logged out: {user.email if user.email else user.username}")
