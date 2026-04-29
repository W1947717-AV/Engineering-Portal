from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('profile/', views.profile_update, name='profile_update'),
    path('change-password/', views.change_password, name='change_password'),
]