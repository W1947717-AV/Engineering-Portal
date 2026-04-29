from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from dashboard_app import views as dashboard_views

urlpatterns = [
    path('', lambda request: redirect('/dashboard/')),

    path('login/', auth_views.LoginView.as_view(
        template_name='login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        template_name='logout.html'
    ), name='logout'),

    path('register/', dashboard_views.register, name='register'),

    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard_app.urls')),
    path('teams/', include('teams.urls')),
    path('messages/', include('messages_app.urls')),
    path('schedule/', include('schedule_app.urls')),

    # Shortcut URLs so /profile/ and /change-password/ work from anywhere
    path('profile/', dashboard_views.profile_update, name='profile'),
    path('change-password/', dashboard_views.change_password, name='change_password'),
]