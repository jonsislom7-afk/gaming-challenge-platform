from rest_framework import views, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import AIGeneratedIdea, AIIdeaFeedback
from .serializers import AIGeneratedIdeaSerializer, AIIdeaFeedbackSerializer
from apps.payments.models import UserSubscription


class AIGeneratedIdeasViewSet(viewsets.ReadOnlyModelViewSet):
    """AI generated ideas - premium streamers uchun"""
    queryset = AIGeneratedIdea.objects.all().order_by('-rating')
    serializer_class = AIGeneratedIdeaSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-rating', '-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # Premium-only ideas - subscription tekshirish
        if user.role == 'STREAMER':
            user_subscription = user.subscription if hasattr(user, 'subscription') else None
            if user_subscription and user_subscription.is_active:
                # Premium - barcha ideas uchun access
                return queryset
            else:
                # Tekin - faqat free ideas
                return queryset.filter(is_premium_only=False)
        
        return queryset.filter(is_premium_only=False)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like AI idea"""
        idea = self.get_object()
        feedback, created = AIIdeaFeedback.objects.get_or_create(
            ai_idea=idea,
            user=request.user
        )
        feedback.is_liked = True
        feedback.save()
        
        # Rating yangilash
        idea.rating = idea.feedbacks.filter(is_liked=True).count()
        idea.save()
        
        return Response(AIGeneratedIdeaSerializer(idea).data)
    
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """Unlike AI idea"""
        idea = self.get_object()
        try:
            feedback = AIIdeaFeedback.objects.get(
                ai_idea=idea,
                user=request.user
            )
            feedback.delete()
        except AIIdeaFeedback.DoesNotExist:
            pass
        
        # Rating yangilash
        idea.rating = idea.feedbacks.filter(is_liked=True).count()
        idea.save()
        
        return Response(AIGeneratedIdeaSerializer(idea).data)


class AIIdeasListView(views.APIView):
    """Get AI ideas with pagination"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        
        if user.role == 'STREAMER':
            user_subscription = user.subscription if hasattr(user, 'subscription') else None
            if user_subscription and user_subscription.is_active:
                ideas = AIGeneratedIdea.objects.all()
            else:
                ideas = AIGeneratedIdea.objects.filter(is_premium_only=False)
        else:
            ideas = AIGeneratedIdea.objects.filter(is_premium_only=False)
        
        ideas = ideas.order_by('-rating', '-created_at')
        
        total = ideas.count()
        start = (page - 1) * limit
        end = start + limit
        
        paginated_ideas = ideas[start:end]
        
        return Response({
            'count': total,
            'page': page,
            'limit': limit,
            'results': AIGeneratedIdeaSerializer(paginated_ideas, many=True).data
        })
