import base64
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
            avatar_file = request.FILES.get('avatar')

            data = {k: v for k, v in request.data.items() if k != 'avatar'}
            serializer = self.get_serializer(self.get_object(), data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            if avatar_file:
                mime = avatar_file.content_type or 'image/jpeg'
                encoded = base64.b64encode(avatar_file.read()).decode('utf-8')
                user.avatar = f'data:{mime};base64,{encoded}'
                user.save(update_fields=['avatar'])

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
