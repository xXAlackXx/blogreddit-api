from django.urls import path
from .views import RegisterView, ProfileView, UserCommentsView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('me/comments/', UserCommentsView.as_view(), name='my-comments'),
]