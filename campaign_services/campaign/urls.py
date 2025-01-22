from django.urls import path, include
from .views import UserCampaignSuperAdminViewSet, UserCampaignAdminViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'campaign-superadmin', UserCampaignSuperAdminViewSet, basename="superadmin-campaigns")
router.register(r'campaign-admin', UserCampaignAdminViewSet, basename="admin-views")

urlpatterns = [
   
    path('', include(router.urls)),
]