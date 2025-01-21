
from django.contrib import admin
from django.urls import path, include
from practice_users import urls as pu_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include(pu_urls)),
    

]
