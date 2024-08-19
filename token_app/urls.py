from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='list_apps'),
    path('signup/', views.signup, name='list_apps'),
]