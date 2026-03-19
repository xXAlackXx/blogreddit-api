from django.urls import path
from .views import PostListCreateView, PostDetailView, CommentListCreateView, CommentDetailView, VoteView

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('<int:post_pk>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    path('<int:post_pk>/comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('<int:pk>/vote/', VoteView.as_view(), name='post-vote'),
]