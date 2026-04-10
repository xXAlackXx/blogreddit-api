from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


User = get_user_model()


class LoginRateThrottle(AnonRateThrottle):
    rate = '5/minute'


class CaseInsensitiveTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Make username case-insensitive for login
        username = attrs.get('username', '')
        if username:
            try:
                # Find user case-insensitively
                user = User.objects.get(username__iexact=username)
                # Replace with the actual username (correct case)
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass  # Let the parent class handle the error
            except User.MultipleObjectsReturned:
                pass  # Edge case, let parent handle

        return super().validate(attrs)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]
    serializer_class = CaseInsensitiveTokenObtainPairSerializer


urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth JWT
    path('api/auth/token/', ThrottledTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/posts/', include('apps.posts.urls')),
    path('api/admin/', include('apps.posts.admin_urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Users
    path('api/users/', include('apps.users.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)