import re
from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    author_avatar = serializers.CharField(source='author.avatar', read_only=True, default=None)
    hashtag = serializers.CharField(max_length=50, required=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'hashtag', 'author', 'author_avatar', 'created_at', 'updated_at', 'upvotes', 'downvotes']
        read_only_fields = ['id', 'author', 'author_avatar', 'created_at', 'updated_at', 'upvotes', 'downvotes']

    def validate_hashtag(self, value):
        value = value.lstrip('#').lower().strip()
        if not re.match(r'^[a-z0-9_]+$', value):
            raise serializers.ValidationError('Solo letras, números y guiones bajos.')
        if len(value) < 2:
            raise serializers.ValidationError('Mínimo 2 caracteres.')
        if len(value) > 30:
            raise serializers.ValidationError('Máximo 30 caracteres.')
        return value

    def validate_image(self, value):
        if value is None:
            return value
        allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed:
            raise serializers.ValidationError('Solo se permiten imágenes JPEG, PNG, GIF o WEBP.')
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('La imagen no puede superar 5 MB.')
        return value

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    author_avatar = serializers.CharField(source='author.avatar', read_only=True, default=None)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_avatar', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'post', 'author', 'author_avatar', 'created_at', 'updated_at']

class AdminCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'post_title', 'author', 'content', 'created_at']
        read_only_fields = fields
