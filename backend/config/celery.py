import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('gaming_challenge')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'generate-daily-challenge': {
        'task': 'apps.challenges.tasks.generate_daily_challenge',
        'schedule': crontab(hour=0, minute=0),  # Har kuni yarim tun
    },
    'update-leaderboard': {
        'task': 'apps.challenges.tasks.update_leaderboard',
        'schedule': crontab(hour='*/6'),  # Har 6 soatda
    },
    'check-expired-subscriptions': {
        'task': 'apps.payments.tasks.check_expired_subscriptions',
        'schedule': crontab(hour='*/12'),  # Har 12 soatda
    },
    'generate-ai-ideas': {
        'task': 'apps.social.tasks.generate_ai_ideas',
        'schedule': crontab(hour=0, minute=0),  # Har kuni yarim tun
    },
}
