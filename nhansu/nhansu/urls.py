# nhansu/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
import views

# TẠM THỜI COMMENT HẾT IMPORT TỪ CÁC APP
# from employees import views as employee_views
# from attendance import views as attendance_views
# from salary import views as salary_views
# from schedule import views as schedule_views
# from reward_penalty import views as reward_penalty_views
# from report import views as report_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # AUTH & DASHBOARD
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard-nv/', views.dashboard_nv, name='dashboard_nv'),

    # COMMENT HẾT CÁC URL CỦA APP - SẼ THÊM SAU KHI CODE XONG VIEWS
    # path('nhanvien/', employee_views.employee_list, name='employee_list'),
    # path('chamcong/', attendance_views.attendance_list, name='attendance_list'),
    # path('luong/', salary_views.salary_list, name='salary_list'),
    # path('lichlam/', schedule_views.schedule_list, name='schedule_list'),
    # path('thuongphat/', reward_penalty_views.reward_penalty_list, name='reward_penalty_list'),
    # path('baocao/', report_views.report_list, name='report_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)