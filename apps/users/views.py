import os
import traceback
import uuid
from urllib.parse import urlparse

import cloudinary
import cloudinary.uploader
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.posts.models import Comment
from .serializers import UserSerializer, RegisterSerializer, UserCommentSerializer

User = get_user_model()


def _cloudinary_upload(file):
    """Upload a file to Cloudinary and return the secure URL."""
    url_str = os.environ.get('CLOUDINARY_URL', '')
    if url_str:
        parsed = urlparse(url_str)
        cloudinary.config(
            cloud_name=parsed.hostname,
            api_key=parsed.username,
            api_secret=parsed.password,
            secure=True,
        )
    result = cloudinary.uploader.upload(
        file,
        folder='avatars',
        resource_type='image',
    )
    return result['secure_url']


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
        try:
            avatar_file = request.FILES.get('avatar')

            # Build data dict without avatar so the serializer never touches it
            data = {k: v for k, v in request.data.items() if k != 'avatar'}

            serializer = self.get_serializer(
                self.get_object(), data=data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            if avatar_file:
                url = _cloudinary_upload(avatar_file)
                # Update avatar directly via queryset to skip the storage backend
                User.objects.filter(pk=user.pk).update(avatar=url)
                user.refresh_from_db()

            return Response(self.get_serializer(user).data)

        except Exception as e:
            return Response(
                {'error': type(e).__name__, 'detail': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserCommentsView(generics.ListAPIView):
    serializer_class = UserCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user).order_by('-created_at')
