
from django.contrib import admin
from django.urls import path, include
from practice_users import urls as pu_urls
from campaign import urls as cu_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include(pu_urls)),
    path('user-campaigns/', include(cu_urls)),
    

]
