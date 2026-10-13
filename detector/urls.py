from django.urls import path
from . import views

app_name = 'detector'

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.scan_history, name='history'),
    path('benchmarks/', views.benchmarks_view, name='benchmarks'),
    path('api/scan/<int:scan_id>/', views.scan_detail_api, name='scan_detail_api'),
    path('scan/<int:scan_id>/delete/', views.delete_scan, name='delete_scan'),
]
