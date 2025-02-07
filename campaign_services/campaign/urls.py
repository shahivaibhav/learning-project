from django.urls import path, include
from .views import UserCampaignSuperAdminViewSet, UserCampaignAdminViewSet, UserMessagesViewSet, SendEmailViewSet, AllSentCampaigns, AcceptOrRejectCampaignViewSet, ScheduleCampaignsViewSet, AllPracticeUsersViewSet, SendAllCampaignsViewSet, MarkAsSeenViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'campaign-superadmin', UserCampaignSuperAdminViewSet, basename="superadmin-campaigns")
router.register(r'campaign-admin', UserCampaignAdminViewSet, basename="admin-views")
router.register(r'messages', UserMessagesViewSet, basename="user-message")
router.register(r'all-sent-messages', AllSentCampaigns, basename="sent-messages")
router.register(r'send-email', SendEmailViewSet, basename="send-emails")
router.register(r'get-practice_users', AllPracticeUsersViewSet, basename="practice-users")
router.register(r'send-all-campaigns', SendAllCampaignsViewSet, basename="all-campaigns")
# router.register(r'seen-messages', MarkAsSeenViewSet, basename="seen-message")


urlpatterns = [
   
    path('api/', include(router.urls)),
    path('api/accept/<int:pk>', AcceptOrRejectCampaignViewSet.as_view({'put': 'update'}), name='accept-reject-campaign'),
    path('api/schedule_campaigns/<int:campaign_id>/', ScheduleCampaignsViewSet.as_view({'post': 'create'}), name='schedule_campaign'),
    path('api/seen-messages', MarkAsSeenViewSet.as_view({'put': 'update'}), name='mark-seen'),
    
]