from celery import shared_task
from django.utils import timezone
from .models import UserSubscription


@shared_task
def check_expired_subscriptions():
    """Tugagan subscription'larni deactivate qilish"""
    now = timezone.now()
    
    expired_subscriptions = UserSubscription.objects.filter(
        is_active=True,
        expires_at__lt=now
    )
    
    count = expired_subscriptions.update(is_active=False)
    return f'{count} subscriptions deactivated'
