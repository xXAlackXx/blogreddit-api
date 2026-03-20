from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'author', 'created_at', 'updated_at', 'upvotes', 'downvotes']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at', 'upvotes', 'downvotes']

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

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'post', 'author', 'created_at', 'updated_at']
