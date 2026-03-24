import base64

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.posts.models import Comment
from .serializers import UserSerializer, RegisterSerializer, UserCommentSerializer

User = get_user_model()

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


class UserCommentsView(generics.ListAPIView):
    serializer_class = UserCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user).order_by('-created_at')
