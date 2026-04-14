from django.urls import path
from . import views

urlpatterns = [
    # Tên định danh (name) PHẢI LÀ 'report_view'
    path('', views.report_view, name='report_view'),
]