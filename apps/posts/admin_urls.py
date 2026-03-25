from django.urls import path
from .views import (
    AdminPostListView, AdminPostDeleteView,
    AdminCommentListView, AdminCommentDeleteView,
    AdminStatsView,
)

urlpatterns = [
    path('stats/',              AdminStatsView.as_view(),          name='admin-stats'),
    path('posts/',              AdminPostListView.as_view(),        name='admin-post-list'),
    path('posts/<int:pk>/',     AdminPostDeleteView.as_view(),      name='admin-post-delete'),
    path('comments/',           AdminCommentListView.as_view(),     name='admin-comment-list'),
    path('comments/<int:pk>/',  AdminCommentDeleteView.as_view(),   name='admin-comment-delete'),
]
