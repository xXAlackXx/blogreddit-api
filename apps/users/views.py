import traceback
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.posts.models import Comment
from .serializers import UserSerializer, RegisterSerializer, UserCommentSerializer

User = get_user_model()


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
            return super().update(request, *args, **kwargs)
        except Exception as e:
            import os, cloudinary
            cfg = cloudinary.config()
            secret = cfg.api_secret or ''
            debug = {
                'error': type(e).__name__,
                'detail': traceback.format_exc(),
                'cloudinary_debug': {
                    'cloud_name': cfg.cloud_name,
                    'api_key': cfg.api_key,
                    'api_secret_len': len(secret),
                    'api_secret_first3': secret[:3],
                    'api_secret_last3': secret[-3:],
                    'CLOUDINARY_URL_set': bool(os.environ.get('CLOUDINARY_URL')),
                },
            }
            return Response(debug, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserCommentsView(generics.ListAPIView):
    serializer_class = UserCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user).order_by('-created_at')