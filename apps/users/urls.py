from django.urls import path
from .views import RegisterView, ProfileView, UserCommentsView, PublicProfileView, PublicUserCommentsView

urlpatterns = [
    path('register/',                    RegisterView.as_view(),          name='register'),
    path('me/',                          ProfileView.as_view(),           name='profile'),
    path('me/comments/',                 UserCommentsView.as_view(),      name='my-comments'),
    path('<str:username>/',              PublicProfileView.as_view(),     name='public-profile'),
    path('<str:username>/comments/',     PublicUserCommentsView.as_view(),name='public-comments'),
]