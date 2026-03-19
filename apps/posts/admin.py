from django.contrib import admin
from .models import Post, Comment, Vote
# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'upvotes', 'downvotes', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'author__username']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at']
    search_fields = ['author__username', 'post__title']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'vote_type', 'created_at']