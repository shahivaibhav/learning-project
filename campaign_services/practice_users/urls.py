from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PracticeUserViewSet

router = DefaultRouter()

router.register(r'practice_user', PracticeUserViewSet, basename='practice_user')

urlpatterns = [
    path('api/', include(router.urls))
]
