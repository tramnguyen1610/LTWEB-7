from django.urls import path
from . import views

urlpatterns = [
    # Chữ 'cham-cong/' đã được cấu hình ở bên ngoài rồi, nên ở đây chỉ cần viết đoạn đuôi thôi
    path('xu-ly/', views.xu_ly_cham_cong, name='xu_ly_cham_cong'),
    path('chinh-sua/', views.chinh_sua_cham_cong, name='chinh_sua_cham_cong'),
    path('xem/', views.xem_cham_cong, name='xem_cham_cong'),
]