from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_home, name='team_home'),
    path('<int:id>/', views.team_detail, name='team_detail'),

    path('departments/', views.departments_home, name='departments_home'),
    path('departments/<int:id>/', views.department_detail, name='department_detail'),
]