import re
from django.contrib.auth import get_user_model
from rest_framework import serializers
from apps.posts.models import Comment
from .models import ProfileTheme

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

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
    posts_count    = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'bio', 'avatar', 'karma', 'created_at', 'posts_count', 'comments_count']


class ProfileThemeSerializer(serializers.ModelSerializer):
    """
    Only scalar fields live here — banner_image (BinaryField) is never
    exposed through this serializer, so save() never touches it.
    Three read-only helpers give the frontend what it needs.
    """
    has_custom_banner = serializers.SerializerMethodField()
    banner_image_url  = serializers.SerializerMethodField()
    banner_gradient   = serializers.SerializerMethodField()

    class Meta:
        model  = ProfileTheme
        # ⚠️ banner_image / banner_image_content_type intentionally absent
        fields = [
            'accent_color', 'banner_preset', 'pattern', 'font',
            'banner_opacity', 'glow_intensity', 'border_accent', 'mood',
            'has_custom_banner', 'banner_image_url', 'banner_gradient',
            'updated_at',
        ]
        read_only_fields = ['has_custom_banner', 'banner_image_url', 'banner_gradient', 'updated_at']

    def get_has_custom_banner(self, obj):
        return bool(obj.banner_image)

    def get_banner_image_url(self, obj):
        if not obj.banner_image:
            return None
        request = self.context.get('request')
        url = f'/api/users/{obj.user_id}/banner-image/'
        return request.build_absolute_uri(url) if request else url

    def get_banner_gradient(self, obj):
        return obj.BANNER_PRESETS.get(obj.banner_preset, obj.BANNER_PRESETS['nebula'])

    # ── validation ──────────────────────────────────────────────────────────

    def validate_accent_color(self, value):
        value = value.strip()
        if not value.startswith('#'):
            value = '#' + value
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError('Must be a valid 6-digit hex color (#RRGGBB)')
        return value.upper()

    def validate_banner_preset(self, value):
        if value not in ProfileTheme.BANNER_PRESETS:
            raise serializers.ValidationError('Invalid banner preset')
        return value

    def validate_font(self, value):
        if value not in [f[0] for f in ProfileTheme.FONT_CHOICES]:
            raise serializers.ValidationError('Invalid font choice')
        return value

    def validate_banner_opacity(self, value):
        if not (20 <= int(value) <= 100):
            raise serializers.ValidationError('Must be 20–100')
        return int(value)

    def validate_glow_intensity(self, value):
        if not (0 <= int(value) <= 100):
            raise serializers.ValidationError('Must be 0–100')
        return int(value)

    def validate_border_accent(self, value):
        if not (0 <= int(value) <= 100):
            raise serializers.ValidationError('Must be 0–100')
        return int(value)

    # ── override update so we only write the changed scalar fields ──────────

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Never include banner_image / banner_image_content_type in update_fields
        instance.save(update_fields=list(validated_data.keys()) + ['updated_at'])
        return instance


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