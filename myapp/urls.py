from django.urls import path
from . import views, metrics

urlpatterns = [
    path('app/', views.create, name='create_app'),
    path('app/<int:app_id>/', views.dispatcher, name='get_app'),
    path('apps/', views.list, name='list_apps'),
    path('metrics/', metrics.metrics_view, name='metrics')
]