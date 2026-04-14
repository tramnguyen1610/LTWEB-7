from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.cham_cong_dashboard, name='dashboard'),
    path('xu-ly/', views.xu_ly_cham_cong, name='xu_ly_cham_cong'),
    path('chinh-sua/', views.chinh_sua_cham_cong, name='chinh_sua_cham_cong'),
    path('xem-chi-tiet/', views.xem_cham_cong, name='xem_cham_cong'),

    # Các API xử lý file Excel
    path('api/check/', views.attendance_check, name='attendance_check'),
    path('api/confirm/', views.attendance_confirm, name='attendance_confirm'),  # DÒNG CÒN THIẾU NÈ!

    # API cập nhật từ popup
    path('api/update/<int:db_id>/', views.update_attendance_api, name='update_api'),
]