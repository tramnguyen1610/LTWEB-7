from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # TRANG CHỦ: Tự động dẫn về Dashboard của quản lý khi vừa mở web
    path('', lambda request: redirect('dashboard_manager'), name='home'),

    # ĐĂNG XUẤT: Trả về trang chủ/login sau khi logout
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # KẾT NỐI APP NHÂN VIÊN
    path('employees/', include('apps.employees.urls')),

    # KẾT NỐI APP CHẤM CÔNG (Có namespace 'attendance')
    path('cham-cong/', include('apps.attendance.urls', namespace='attendance')),

    # KẾT NỐI APP DASHBOARD/ACCOUNTS
    path('dashboard/', include('apps.accounts.urls')),

    path('thuong-phat/', include('apps.reward_penalty.urls')),
    path('bao-cao/', include('apps.report.urls')),
]