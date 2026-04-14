from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),

    path('cham-cong/', include('apps.attendance.urls')),
    path('dashboard/', include('apps.accounts.urls')),
    path('reward-penalty/', include('apps.reward_penalty.urls')),
    path('report/', include('apps.report.urls'))
]