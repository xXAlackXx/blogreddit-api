import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.posts.models import Comment
from .models import ProfileTheme

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(source='post_set.count', read_only=True)
    comments_count = serializers.IntegerField(source='comment_set.count', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'karma', 'role', 'created_at', 'posts_count', 'comments_count']
        read_only_fields = ['id', 'karma', 'role', 'created_at', 'posts_count', 'comments_count']



class UserCommentSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_id    = serializers.IntegerField(source='post.id',    read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'post_title', 'content', 'created_at']
        read_only_fields = fields


class PublicUserSerializer(serializers.ModelSerializer):
    posts_count    = serializers.IntegerField(source='post_set.count',    read_only=True)
    comments_count = serializers.IntegerField(source='comment_set.count', read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'bio', 'avatar', 'karma', 'created_at', 'posts_count', 'comments_count']


class ProfileThemeSerializer(serializers.ModelSerializer):
    has_banner_image = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()
    mood_display     = serializers.SerializerMethodField()
    banner_css       = serializers.SerializerMethodField()
    pattern_css      = serializers.SerializerMethodField()
    css_vars         = serializers.SerializerMethodField()

    class Meta:
        model  = ProfileTheme
        fields = [
            'accent_color', 'banner_preset', 'has_banner_image', 'banner_image_url',
            'pattern', 'font', 'banner_opacity', 'glow_intensity', 'border_accent',
            'mood', 'mood_display', 'banner_css', 'pattern_css', 'css_vars',
        ]
        read_only_fields = [
            'has_banner_image', 'banner_image_url', 'mood_display',
            'banner_css', 'pattern_css', 'css_vars',
        ]

    # --- read-only computed fields ---

    def get_has_banner_image(self, obj):
        return bool(obj.banner_image)

    def get_banner_image_url(self, obj):
        return f'/api/users/{obj.user_id}/banner-image/' if obj.banner_image else None

    def get_mood_display(self, obj):
        return obj.get_mood_display()

    def get_banner_css(self, obj):
        return obj.get_banner_css()

    def get_pattern_css(self, obj):
        return obj.get_pattern_css()

    def get_css_vars(self, obj):
        return obj.get_css_vars()

    # --- validation ---

    def validate_accent_color(self, value):
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError('Must be a valid hex color (#RRGGBB)')
        return value.upper()

    def validate_banner_preset(self, value):
        if value not in ProfileTheme.BANNER_PRESETS:
            raise serializers.ValidationError('Invalid banner preset')
        return value

    def validate_font(self, value):
        valid = [f[0] for f in ProfileTheme.FONT_CHOICES]
        if value not in valid:
            raise serializers.ValidationError('Invalid font')
        return value

    def validate_banner_opacity(self, value):
        if not (20 <= value <= 100):
            raise serializers.ValidationError('Must be 20–100')
        return value

    def validate_glow_intensity(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError('Must be 0–100')
        return value

    def validate_border_accent(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError('Must be 0–100')
        return value


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