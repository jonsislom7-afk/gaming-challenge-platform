from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta
import random
from .models import Challenge, DailyChallenge, UserChallenge, Leaderboard
from apps.leaderboard.models import Leaderboard


@shared_task
def generate_daily_challenge():
    """Har kuni yangi challenge yaratish"""
    today = date.today()
    
    # Bugun uchun daily challenge mavjudmi?
    if DailyChallenge.objects.filter(date=today).exists():
        return 'Daily challenge already exists'
    
    # Tasdig'langan challenge'lardan birini tanlash
    approved_challenges = Challenge.objects.filter(status='APPROVED')
    
    if approved_challenges.exists():
        challenge = random.choice(list(approved_challenges))
        DailyChallenge.objects.create(
            challenge=challenge,
            date=today
        )
        return f'Daily challenge created: {challenge.title}'
    
    return 'No approved challenges found'


@shared_task
def update_leaderboard():
    """Leaderboard'ni yangilash"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Barcha streamers uchun
    streamers = User.objects.filter(role='STREAMER')
    
    for period in ['DAILY', 'WEEKLY', 'MONTHLY', 'ALL_TIME']:
        # User challenges'ni hisoblash
        user_scores = {}
        
        for streamer in streamers:
            if period == 'DAILY':
                completed = UserChallenge.objects.filter(
                    user=streamer,
                    status='COMPLETED',
                    completed_at__date=date.today()
                ).count()
                points = UserChallenge.objects.filter(
                    user=streamer,
                    status='COMPLETED',
                    completed_at__date=date.today()
                ).aggregate(total=models.Sum('points_earned'))['total'] or 0
            elif period == 'WEEKLY':
                week_start = date.today() - timedelta(days=date.today().weekday())
                completed = UserChallenge.objects.filter(
                    user=streamer,
                    status='COMPLETED',
                    completed_at__date__gte=week_start
                ).count()
                points = UserChallenge.objects.filter(
                    user=streamer,
                    status='COMPLETED',
                    completed_at__date__gte=week_start
                ).aggregate(total=models.Sum('points_earned'))['total'] or 0
            elif period == 'MONTHLY':
                today_date = date.today()
                month_start = date(today_date.year, today_date.month, 1)
                completed = UserChallenge.objects.filter(
                    user=streamer,
                    status='COMPLETED',
                    completed_at__date__gte=month_start
                ).count()
                points = UserChallenge.objects.filter(
                    user=streamer,
                    status='COMPLETED',
                    completed_at__date__gte=month_start
                ).aggregate(total=models.Sum('points_earned'))['total'] or 0
            else:  # ALL_TIME
                completed = UserChallenge.objects.filter(
                    user=streamer,
                    status='COMPLETED'
                ).count()
                points = streamer.total_points
            
            user_scores[streamer.id] = {'points': points, 'completed': completed}
        
        # Rank assignment
        sorted_users = sorted(
            user_scores.items(),
            key=lambda x: x[1]['points'],
            reverse=True
        )
        
        for rank, (user_id, score_data) in enumerate(sorted_users, 1):
            Leaderboard.objects.update_or_create(
                user_id=user_id,
                period=period,
                defaults={
                    'rank': rank,
                    'points': score_data['points'],
                    'challenges_completed': score_data['completed']
                }
            )
    
    return 'Leaderboard updated'
