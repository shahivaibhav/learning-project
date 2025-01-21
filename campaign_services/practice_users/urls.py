from django.urls import path, include
from .views import RegisterView, LoginView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),  # Signup endpoint
    path('api/login/', LoginView.as_view(), name='login'),          # Login endpoint
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
