from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def ensure_user_profile_for_admin_accounts(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.is_superuser:
        UserProfile.objects.get_or_create(user=instance, defaults={"role": "admin"})
    elif instance.is_staff:
        UserProfile.objects.get_or_create(user=instance, defaults={"role": "hr"})
