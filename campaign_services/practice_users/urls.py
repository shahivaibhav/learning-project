from django.urls import path, include
from .views import RegisterView, LoginView, ResetPasswordView, session_status, logout_view, GetUserRoleView, AllPracticeUser

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # Signup endpoint
    path('login/', LoginView.as_view(), name='login'),          # Login endpoint
    path('reset-password/', ResetPasswordView.as_view(), name='rest-password'),          # Login endpoint
    path('session-status/', session_status, name='session'),
    path('logout/', logout_view, name='logout'),
    path('get_user_role/', GetUserRoleView.as_view(), name='role'),
    path('all-practice-users/', AllPracticeUser.as_view({'get': 'list'}), name='practices'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
