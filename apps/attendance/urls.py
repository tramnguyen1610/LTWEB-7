from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Các trang giao diện
    path('', views.cham_cong_dashboard, name='cham_cong'),
    path('xu-ly/', views.xu_ly_cham_cong, name='xu_ly_cham_cong'),
    path('chinh-sua/', views.chinh_sua_cham_cong, name='chinh_sua_cham_cong'),
    path('xem-chi-tiet/', views.xem_cham_cong, name='xem_cham_cong'),

    # Các API xử lý dữ liệu (Upload, Xác nhận, Chỉnh sửa)
    path('api/check/', views.attendance_check, name='attendance_check'),
    path('api/confirm/', views.attendance_confirm, name='attendance_confirm'),
    path('api/update/<int:db_id>/', views.update_attendance_api, name='update_api'),
]