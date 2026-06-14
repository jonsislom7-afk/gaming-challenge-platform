from celery import shared_task
from django.conf import settings
from .models import AIGeneratedIdea
import openai
import os

# OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

GAME_CATEGORIES = [
    'First Person Shooter (FPS)',
    'Role Playing Game (RPG)',
    'Strategy',
    'Puzzle',
    'Multiplayer Online Battle Arena (MOBA)',
    'Racing',
    'Sports',
    'Horror',
    'Adventure',
    'Simulation'
]

DIFFICULTIES = ['EASY', 'MEDIUM', 'HARD', 'EXPERT']


@shared_task
def generate_ai_ideas():
    """AI yordamida challenge idealar yaratish"""
    
    if not settings.OPENAI_API_KEY:
        return 'OpenAI API key not configured'
    
    try:
        ideas_created = 0
        
        # 3 ta idea yaratish
        for _ in range(3):
            import random
            category = random.choice(GAME_CATEGORIES)
            difficulty = random.choice(DIFFICULTIES)
            
            prompt = f"""Create a creative gaming challenge for a {category} game.
            Difficulty level: {difficulty}
            
            Please provide:
            1. Challenge title (short)
            2. Challenge description (detailed, 2-3 sentences)
            
            Format: TITLE: [title]\nDESCRIPTION: [description]"""
            
            response = openai.ChatCompletion.create(
                model=settings.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response['choices'][0]['message']['content']
            
            # Parse response
            lines = content.split('\n')
            title = lines[0].replace('TITLE: ', '').strip() if len(lines) > 0 else 'AI Challenge'
            description = lines[1].replace('DESCRIPTION: ', '').strip() if len(lines) > 1 else 'No description'
            
            # Create idea
            AIGeneratedIdea.objects.create(
                title=title,
                description=description,
                game_category=category,
                difficulty=difficulty,
                ai_model=settings.AI_MODEL,
                ai_prompt=prompt,
                is_premium_only=True  # Eng yaxshi idealar - premium uchun
            )
            ideas_created += 1
        
        return f'{ideas_created} AI ideas generated'
    
    except Exception as e:
        return f'Error generating AI ideas: {str(e)}'


@shared_task
def generate_ai_idea_on_demand(category=None, difficulty=None):
    """On-demand AI idea generation"""
    
    if not settings.OPENAI_API_KEY:
        return None
    
    try:
        import random
        category = category or random.choice(GAME_CATEGORIES)
        difficulty = difficulty or random.choice(DIFFICULTIES)
        
        prompt = f"""Create a creative gaming challenge for a {category} game.
        Difficulty level: {difficulty}
        
        Please provide:
        1. Challenge title (short)
        2. Challenge description (detailed, 2-3 sentences)
        
        Format: TITLE: [title]\nDESCRIPTION: [description]"""
        
        response = openai.ChatCompletion.create(
            model=settings.AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200
        )
        
        content = response['choices'][0]['message']['content']
        
        # Parse response
        lines = content.split('\n')
        title = lines[0].replace('TITLE: ', '').strip() if len(lines) > 0 else 'AI Challenge'
        description = lines[1].replace('DESCRIPTION: ', '').strip() if len(lines) > 1 else 'No description'
        
        # Create idea
        idea = AIGeneratedIdea.objects.create(
            title=title,
            description=description,
            game_category=category,
            difficulty=difficulty,
            ai_model=settings.AI_MODEL,
            ai_prompt=prompt,
            is_premium_only=True
        )
        
        return idea.id
    
    except Exception as e:
        return None
