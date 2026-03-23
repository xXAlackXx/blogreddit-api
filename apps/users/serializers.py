from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.posts.models import Comment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(source='post_set.count', read_only=True)
    comments_count = serializers.IntegerField(source='comment_set.count', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'karma', 'created_at', 'posts_count', 'comments_count']
        read_only_fields = ['id', 'karma', 'created_at', 'posts_count', 'comments_count']



class UserCommentSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_id    = serializers.IntegerField(source='post.id',    read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'post_title', 'content', 'created_at']
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)