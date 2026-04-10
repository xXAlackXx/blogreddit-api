from django.urls import path
from .views import (
    RegisterView, ProfileView, UserCommentsView,
    PublicProfileView, PublicUserCommentsView,
    ThemeView, PublicThemeView,
    BannerImageView, BannerUploadView,
)

urlpatterns = [
    path('register/',                    RegisterView.as_view(),          name='register'),
    path('me/',                          ProfileView.as_view(),           name='profile'),
    path('me/comments/',                 UserCommentsView.as_view(),      name='my-comments'),
    path('me/theme/',                    ThemeView.as_view(),             name='my-theme'),
    path('me/theme/banner/',             BannerUploadView.as_view(),      name='banner'),  # POST + DELETE
    path('<int:user_id>/banner-image/',  BannerImageView.as_view(),       name='banner-image'),
    path('<str:username>/theme/',        PublicThemeView.as_view(),       name='public-theme'),
    path('<str:username>/',              PublicProfileView.as_view(),     name='public-profile'),
    path('<str:username>/comments/',     PublicUserCommentsView.as_view(),name='public-comments'),
]