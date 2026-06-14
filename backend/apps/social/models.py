from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AIGeneratedIdea(models.Model):
    """AI tomonidan yaratilgan idealar"""
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
        ('EXPERT', 'Expert'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    game_category = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    
    # AI model info
    ai_model = models.CharField(max_length=50)  # GPT-4, Claude, Groq, etc.
    ai_prompt = models.TextField()  # Qanday prompt ishlatildi
    
    # Rating va feedback
    rating = models.IntegerField(default=0)  # Like'lar soni
    views = models.IntegerField(default=0)
    is_premium_only = models.BooleanField(
        default=True,
        help_text="Faqat premium streamer'lar uchun"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_generated_ideas'
        ordering = ['-rating', '-created_at']
    
    def __str__(self):
        return self.title


class AIIdeaFeedback(models.Model):
    """AI idealariga feedback (rating)"""
    ai_idea = models.ForeignKey(
        AIGeneratedIdea,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_idea_feedbacks',
        limit_choices_to={'role': 'STREAMER'}
    )
    
    is_liked = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_idea_feedbacks'
        unique_together = ['ai_idea', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.ai_idea.title}"
