# apps/attendance/urls.py
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Giao diện
    path('xu-ly/', views.xu_ly_cham_cong, name='xu_ly_cham_cong'),
    path('chinh-sua/', views.chinh_sua_cham_cong, name='chinh_sua_cham_cong'),
    path('xem/', views.xem_cham_cong, name='xem_cham_cong'),

    # API endpoints
    path('api/check/', views.attendance_check, name='attendance_check'),
    path('api/confirm/', views.attendance_confirm, name='attendance_confirm'),
    path('api/detail/<int:employee_id>/', views.employee_attendance_detail, name='employee_attendance_detail'),
    path('api/update/<int:attendance_id>/', views.update_attendance, name='update_attendance'),
    path('api/delete/<int:attendance_id>/', views.delete_attendance, name='delete_attendance'),
]