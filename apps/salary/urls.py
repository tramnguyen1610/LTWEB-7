from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'salary'

urlpatterns = [
    # Trang chủ Lương (trỏ về Dashboard quản lý)
    path('', lambda request: redirect('dashboard_manager'), name='luong'),

    # Trang danh sách lương
    path('thong-tin-luong/', views.xem_thong_tin_luong, name='xem_thong_tin_luong'),
    path('api/danh-sach-luong/', views.api_danh_sach_luong, name='api_danh_sach_luong'),

    # --- 2 ĐƯỜNG LINK MỚI THÊM VÀO ---
    path('thiet-lap-muc-luong/', views.thiet_lap_muc_luong, name='thiet_lap_muc_luong'),
    path('cap-nhat-muc-luong/', views.cap_nhat_muc_luong, name='cap_nhat_muc_luong'),
# THÊM 3 DÒNG NÀY CHO TÍNH LƯƠNG
    path('tinh-luong/', views.tinh_luong, name='tinh_luong'),
    path('api/preview-tinh-luong/', views.api_preview_tinh_luong, name='api_preview_tinh_luong'),
    path('api/thuc-hien-tinh-luong/', views.api_thuc_hien_tinh_luong, name='api_thuc_hien_tinh_luong'),
    path('ket-qua-tinh-luong/', views.ket_qua_tinh_luong, name='ket_qua_tinh_luong'),
    path('api/luu-bang-luong/', views.api_luu_bang_luong, name='api_luu_bang_luong'),
]