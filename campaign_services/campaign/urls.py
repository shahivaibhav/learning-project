from django.urls import path, include
from .views import UserCampaignSuperAdminViewSet, UserCampaignAdminViewSet, UserMessagesViewSet, SendEmailViewSet, AllSentCampaigns, AcceptOrRejectCampaignViewSet, ScheduleCampaignsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'campaign-superadmin', UserCampaignSuperAdminViewSet, basename="superadmin-campaigns")
router.register(r'campaign-admin', UserCampaignAdminViewSet, basename="admin-views")
router.register(r'messages', UserMessagesViewSet, basename="user-message")
router.register(r'all-sent-messages', AllSentCampaigns, basename="sent-messages")


urlpatterns = [
   
    path('api/', include(router.urls)),
    path('api/send-email/<int:campaign_id>/', SendEmailViewSet.as_view({'post': 'create'}), name='send-email'),
    path('api/accept/<int:pk>', AcceptOrRejectCampaignViewSet.as_view({'put': 'update'}), name='accept-reject-campaign'),
    path('api/schedule_campaigns/<int:campaign_id>/', ScheduleCampaignsViewSet.as_view({'post': 'create'}), name='schedule_campaign'),
    
]