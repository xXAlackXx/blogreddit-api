import base64

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.models import Comment
from .models import ProfileTheme
from .serializers import (
    UserSerializer, RegisterSerializer, UserCommentSerializer,
    PublicUserSerializer, ProfileThemeSerializer,
)

User = get_user_model()

ALLOWED_BANNER_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
MAX_BANNER_BYTES     = 3 * 1024 * 1024  # 3 MB

ALLOWED_AVATAR_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
MAX_AVATAR_BYTES = 2 * 1024 * 1024  # 2 MB


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        avatar_file = request.FILES.get('avatar')

        if avatar_file:
            if avatar_file.content_type not in ALLOWED_AVATAR_TYPES:
                return Response(
                    {'avatar': 'Only JPEG, PNG, GIF, and WEBP images are allowed.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if avatar_file.size > MAX_AVATAR_BYTES:
                return Response(
                    {'avatar': 'Avatar must be 2 MB or less.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        data = {k: v for k, v in request.data.items() if k != 'avatar'}
        serializer = self.get_serializer(self.get_object(), data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if avatar_file:
            mime = avatar_file.content_type
            encoded = base64.b64encode(avatar_file.read()).decode('utf-8')
            user.avatar = f'data:{mime};base64,{encoded}'
            user.save(update_fields=['avatar'])

        return Response(self.get_serializer(user).data)


class PublicProfileView(generics.RetrieveAPIView):
    serializer_class   = PublicUserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = 'username'
    queryset           = User.objects.all()


class PublicUserCommentsView(generics.ListAPIView):
    serializer_class   = UserCommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = generics.get_object_or_404(User, username=self.kwargs['username'])
        return Comment.objects.filter(author=user).order_by('-created_at')


class UserCommentsView(generics.ListAPIView):
    serializer_class = UserCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user).order_by('-created_at')


# ── Profile Theme ────────────────────────────────────────────────────────────

class ThemeView(generics.RetrieveUpdateAPIView):
    """GET + PATCH /api/users/me/theme/  — own theme"""
    serializer_class   = ProfileThemeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        theme, _ = ProfileTheme.objects.get_or_create(user=self.request.user)
        return theme

    def update(self, request, *args, **kwargs):
        theme = self.get_object()
        serializer = self.get_serializer(theme, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicThemeView(generics.RetrieveAPIView):
    """GET /api/users/<username>/theme/  — public read of another user's theme"""
    serializer_class   = ProfileThemeSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        user  = generics.get_object_or_404(User, username=self.kwargs['username'])
        theme, _ = ProfileTheme.objects.get_or_create(user=user)
        return theme


class BannerImageView(APIView):
    """GET /api/users/<user_id>/banner-image/  — serve binary banner from DB"""
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        theme = generics.get_object_or_404(ProfileTheme, user_id=user_id)
        if not theme.banner_image:
            return HttpResponse(status=404)
        resp = HttpResponse(
            bytes(theme.banner_image),
            content_type=theme.banner_image_content_type or 'image/jpeg',
        )
        resp['Cache-Control'] = 'public, max-age=3600'
        return resp


class BannerUploadView(APIView):
    """POST /api/users/me/theme/banner/  — upload a custom banner image"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        theme, _ = ProfileTheme.objects.get_or_create(user=request.user)
        file = request.FILES.get('banner_image')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        if file.size > MAX_BANNER_BYTES:
            return Response({'error': 'File too large (max 3 MB)'}, status=status.HTTP_400_BAD_REQUEST)
        if file.content_type not in ALLOWED_BANNER_TYPES:
            return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
        theme.banner_image              = file.read()
        theme.banner_image_content_type = file.content_type
        theme.save(update_fields=['banner_image', 'banner_image_content_type', 'updated_at'])
        return Response({
            'status': 'ok',
            'banner_image_url': f'/api/users/{request.user.id}/banner-image/',
        })


class BannerRemoveView(APIView):
    """POST /api/users/me/theme/banner/remove/  — revert to gradient preset"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        theme, _ = ProfileTheme.objects.get_or_create(user=request.user)
        theme.banner_image              = None
        theme.banner_image_content_type = None
        theme.save(update_fields=['banner_image', 'banner_image_content_type', 'updated_at'])
        return Response({'status': 'ok'})
