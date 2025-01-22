from django.urls import path, include
from .views import RegisterView, LoginView, ResetPasswordView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),  # Signup endpoint
    path('api/login/', LoginView.as_view(), name='login'),          # Login endpoint
    path('api/reset-password/', ResetPasswordView.as_view(), name='rest-password'),          # Login endpoint
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
