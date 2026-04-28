from django.urls import path
from . import views

urlpatterns = [
    path('', views.schedule_home, name='schedule_home'),
    path('new/', views.create_meeting, name='create_meeting'),
    path('<int:id>/accept/', views.accept_meeting, name='accept_meeting'),
    path('<int:id>/decline/', views.decline_meeting, name='decline_meeting'),
    path('<int:id>/delete/', views.delete_meeting, name='delete_meeting'),
]