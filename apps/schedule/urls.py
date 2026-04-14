from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.schedule_register, name='dangkylichlam'),
    path('approve/', views.schedule_approve, name='duyetlichlam'),
    path('tao-lich/', views.tao_lich_lam_viec, name='taolichlamviec'),
    path('xem-lich/', views.lichlam, name='xemlichlamviec'),
    path('api/capacity/', views.api_capacity, name='api_capacity'),
    path('api/xem-lich/<int:employee_id>/', views.api_schedule_detail, name='api_schedule_detail'),
    path('xoa-lich/', views.xoa_lich_lam_viec, name='xoalichlamviec'),
    path('api/delete-schedule/weeks/', views.api_delete_schedule_weeks, name='api_delete_schedule_weeks'),
    path('api/delete-schedule/week-detail/<int:week_id>/', views.api_delete_schedule_week_detail, name='api_delete_schedule_week_detail'),
    path('api/delete-schedule/delete/', views.api_delete_schedule_delete, name='api_delete_schedule_delete'),
    path('duyet-lich/', views.duyet_lich_lam_viec, name='duyetlichlam'),
    path('api/approve-schedule/list/', views.api_approve_schedule_list, name='api_approve_schedule_list'),
    path('api/approve-schedule/update/', views.api_approve_schedule_update, name='api_approve_schedule_update'),
]