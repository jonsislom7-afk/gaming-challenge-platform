from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.GameCategoryViewSet, basename='categories')

urlpatterns = [
    path('daily/', views.DailyChallengeView.as_view(), name='daily-challenges'),
    path('create/', views.CreateChallengeView.as_view(), name='create-challenge'),
    path('my-challenges/', views.UserChallengeListView.as_view(), name='my-challenges'),
    path('<int:challenge_id>/submit/', views.SubmitChallengeView.as_view(), name='submit-challenge'),
    path('user-challenge/<int:user_challenge_id>/complete/', views.CompleteChallengeView.as_view(), name='complete-challenge'),
    path('<int:challenge_id>/report/', views.ReportChallengerView.as_view(), name='report-challenger'),
] + router.urls
